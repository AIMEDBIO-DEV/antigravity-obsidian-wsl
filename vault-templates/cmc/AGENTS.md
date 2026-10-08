# AIMEDBIO CMC Obsidian Vault — 에이전트 공통 지침

`AGENTS.md`가 정책 정본이다. `CLAUDE.md`와 `GEMINI.md`는 이 파일의 symlink다.
노트를 편집한 뒤에는 반드시 다음 단일 검증을 통과시킨다.

```bash
bash scripts/validate-vault.sh
```

## 사용자와 문체

- 사용자: <이름>, AIMEDBIO <직함>  # ← 셋업 시 본인 정보로 교체 (SETUP.md 참고)
- 한국어로 응답하고 영문 파일명과 CMC/GxP 약어를 그대로 사용한다.
- CoC, NiRA, MBR, IPR, DP, DS, USP, DSP, BDS, BMR, GMP, QC, QA, CDMO, CDA, SBL, BI 등 업계 약어를 불필요하게 풀어쓰지 않는다.
- 이모지는 사용자가 요청할 때만 사용한다.
- 한국어 파일은 UTF-8 no BOM으로 유지한다.

## 구조의 단일 소스

- 기계 판정 규칙: `config/vault-schema.yaml`
- 신규 노트 골격: `Templates/`
- Obsidian 문법: repo skill `obsidian-markdown`
- 최종 판정: `scripts/validate-vault.sh`
- 템플릿을 에이전트가 직접 복사할 때는 모든 `<% ... %>` token을 실제 값으로 치환한다.

OKF v0.2 hard conformance를 따른다. 모든 concept note에는 parseable YAML frontmatter와 non-empty `type`이 필요하다. `index.md`와 `log.md`는 reserved file 규칙을 따른다.

`sources`, `generated`, `verified`, `stale_after`는 선택 필드지만 사용할 때는 사실만 기록한다.

- `sources[].resource`는 필수다. 본문 claim attribution은 같은 `sources[].id`를 쓰는 footnote로 연결한다.
- `generated.by`는 `human:<id>`, `process:<id>`, `<producer>/<version>` 중 하나다.
- `verified`는 실제 검증이 끝났을 때만 기록하고 추정하여 채우지 않는다.
- legacy `timestamp`와 본문 `# Citations`를 새로 만들지 않는다. 각각 `generated.at`, `sources`를 쓴다.
- 기존 `status`는 프로젝트·이메일 workflow를 위한 vault extension이다. 허용값은 schema를 따른다.

## 파일 배치와 명명

- 새 노트를 vault root에 만들지 않는다. schema의 note folder에 배치한다.
- Daily는 반드시 `Daily/YYYY-MM-DD.md` 한 경로만 사용한다. 같은 날짜가 있으면 병합한다.
- Projects는 `Projects/P-*.md`, Meetings는 `Meetings/M-*.md`, 이메일은 `Email_Drafts/` 관례를 따른다.
- 파일명은 `Title_Case_With_Underscores` 또는 각 folder의 기존 관례를 따른다.
- 같은 내용의 버전 파일을 늘리지 말고 기존 노트를 갱신한다.
- 새 파일은 빈 파일로 남기지 않는다.

## Frontmatter와 태그

- `type`은 단수 개념명으로 작성한다. folder별 허용 type은 schema를 따른다.
- `tags`를 쓰면 반드시 YAML list여야 하며, 새 태그를 만들기 전에 schema의 `known_tags`를 확인한다.
- 1개 노트에만 쓸 태그는 만들지 않는다. type, status, 구조화 필드 또는 노트 제목으로 충분한지 먼저 본다.
- 프로젝트 코드·회사·제품·사람은 태그가 아니라 전용 노트와 `company`/`project`/`product`/`contact-person` wikilink로 연결한다.
- `type`과 같은 의미의 태그 및 모든 노트에 해당하는 `CMC` 태그를 만들지 않는다.
- 프로젝트 상태의 단일 소스는 frontmatter `status`다. 상태를 바꾸면 `Projects MOC.md` 위치도 맞춘다.

## Wikilink

- vault 내부는 `[[Note]]`, 외부 URL은 Markdown link를 사용한다. OKF export에서만 내부 링크를 표준 Markdown link로 변환한다.
- 링크 전에 대상 노트가 실제로 존재하는지 확인한다. 없는 대상을 조용히 생성하거나 깨진 링크를 남기지 않는다.
- People, Organizations, Products 파일명은 영문을 사용하고 한글 이름은 `aliases`에 둔다.
- 한글 표시는 `[[Huntaek Jung|정훈택]]`처럼 정식 영문 파일명에 alias pipe를 쓴다.
- 구조화 frontmatter에는 pipe 없이 정식 파일명을 쓴다: `"[[Huntaek Jung]]"`.
- 영문 이름을 모르면 임의 로마자 표기를 만들지 말고 사용자에게 확인한다.
- 문서 전체 무조건 치환으로 중첩 wikilink를 만들지 않는다. 기존 `[[...]]` 밖의 완전한 token만 수정한다.

## Daily와 Tasks

- 시스템 current date를 오늘로 사용하되 사용자가 지정한 날짜가 우선이다.
- 미완료 `- [ ]`, 완료 `- [x] ✅ YYYY-MM-DD`, 이월 `- [>]`, 마감 `📅 YYYY-MM-DD`, 대기 `#status/waiting` 문법을 쓴다.
- 오늘 노트가 없으면 최신 이전 Daily의 미완료·대기 항목을 검토하여 이월한다.
- 타인에게 업무를 이관하면 Daily에서는 원래 섹션에서 빼서 `### 👥 타인 이관 완료` 섹션으로 옮기고 `- [x] **텍스트** ✅ YYYY-MM-DD — [[받는사람]]에게 이관 완료 (실제 상태 요약)`로 적는다. 이 `[x]`는 "내 몫이 끝남"을 뜻할 뿐 실제 작업 완료가 아니다. 해당 업무의 단일 소스인 프로젝트 노트는 실제로 끝나지 않았다면 체크박스를 `[ ]`(및 `#status/waiting`)로 그대로 두고, 문구에 "담당 [[받는사람]]에게 이관 ✅ YYYY-MM-DD"만 덧붙인다. Daily와 프로젝트 노트가 서로 다른 완료 상태를 기록하지 않도록 이관 시 두 곳을 함께 갱신한다.

## 이메일

- 이메일 초안과 발송 기록은 `Email_Drafts/`에만 둔다.
- Outlook에 복사할 `subject`와 본문은 plain text로 작성하고 wikilink를 넣지 않는다.
- 연결 정보는 frontmatter의 `project`, `company`, `contact-person`에 둔다.
- 서명은 Outlook이 추가하므로 `Best regards,` 이하를 작성하지 않는다.
- placeholder를 남긴 초안은 발송 가능한 상태로 표시하지 않는다.
- 수정본은 별도 버전 파일보다 같은 노트를 갱신하고 `draft`, `sent`, `superseded` 상태를 명시한다.

## Office 파일

- `.pptx`/`.docx`/`.xlsx`를 파일 보기 도구로 열거나 채팅 첨부로 모델에 넘기지 않는다. 모델 API(예: Vertex AI Gemini)가 Office MIME 타입을 거부해 요청 전체가 `400 INVALID_ARGUMENT`로 실패한다.
- 대신 `officecli`로 텍스트·구조를 꺼내 읽는다: `officecli view <file> outline`, `officecli view <file> text`, `officecli get <file> '/slide[1]' --depth 1`.
- 레이아웃·디자인을 눈으로 봐야 하면 사용자에게 PDF나 이미지로 내보내 달라고 요청한다.

## 작업 종료

1. 의도한 파일만 변경했는지 `git status`와 diff를 확인한다.
2. `bash scripts/validate-vault.sh`를 실행한다.
3. 실패를 해결하기 전에는 커밋하지 않는다.
4. 사용자 변경과 무관한 dirty file은 수정·정리·커밋하지 않는다.
