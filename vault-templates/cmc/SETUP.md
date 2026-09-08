---
type: reference
status: stable
---

# CMC Vault 초기 셋업

CMC팀 Obsidian vault의 작성 규칙·검증·템플릿 골격이다.
노트 내용은 들어 있지 않고, 규칙과 폴더 구조만 있다.
셋업을 마치면 `bash scripts/validate-vault.sh`가 OK로 통과해야 한다.

## 1. 사전 준비

- Obsidian 최신 버전
- Python 3.10+ (검증 스크립트용)
- git

## 2. 설치된 보관함 확인

`setup.sh --profile cmc`가 선택한 경로에 이 파일과 규칙을 설치하고 Obsidian에 등록한다.
기본 경로는 `~/Obsidian/CMC`이며 실제 경로는 설치 완료 메시지 또는 install.json에서 확인한다.
이미 설치된 폴더를 다시 mv하거나 기존 보관함을 덮어쓰지 않는다.

`CLAUDE.md`, `GEMINI.md`, `.agents/skills` symlink는 적용기가 만든다.
Git으로 관리하려면 이 보관함 폴더에서 `git init` 후 아래 hook을 설치한다(선택).

## 3. Obsidian에서 vault 열기

Obsidian → "Open folder as vault" → 위 폴더 선택.
첫 실행에서 **Trust author and enable plugins**로 이 번들의 플러그인 사용을 허용한다.
허용 전에는 다음 플러그인들이 실행되지 않는다.

- Minimal 테마 + Minimal Settings
- Templater (folder 매핑 설치, 자동 실행 허용은 아래 PC별 단계 필요), core Templates는 꺼진 상태
- Daily notes 폴더 `Daily/`, 형식 `YYYY-MM-DD`
- 검색 제외 경로: `Templates/`, `scripts/`, `config/`

플러그인은 고정 버전으로 설치된다. 다른 버전으로 업데이트하면 적용기가 충돌을 보고할 수 있으므로
팀 배포본의 버전 갱신과 함께 맞춘다.

### 반드시 각 PC에서 할 일

1. Settings → Templater를 연다.
2. **Trigger Templater on new file creation**을 켠다.
3. 표시된 설명을 확인하고 허용한다. 이 값은 보관함 파일이 아닌 **장치별 저장소**에 저장된다.
4. Template matching mode가 **Folder templates**이고 아래 8개 매핑이 보이는지 확인한다.
5. Projects 폴더의 New note와 Daily 버튼으로 실제 생성 시험을 한다.

설치기는 이 허용 절차를 우회하거나 local storage를 강제로 복사하지 않는다.
`agy`는 이 단계를 안내하고 실제 결과를 확인한 뒤 완료로 보고한다.
validator 성공만으로 플러그인 실행 허용까지 완료됐다고 가정하지 않는다.

배포 템플릿에는 커서 이동 토큰을 넣지 않는다. 제목·날짜 치환 후 해석되지 않은 token이 없어야 한다.
다음 조건을 유지해야 검증을 통과한다.

- `templates_folder` = `Templates`
- trigger mode = folder mapping
- folder mapping 8개가 `config/vault-schema.yaml`의 `note_folders`와 정확히 1:1
- system command / user script 경로는 비워 둔다

## 4. 검증 환경

```bash
sudo apt install python3-yaml            # setup.sh는 의존성 단계에서 이미 설치함
bash scripts/install-hooks.sh             # 커밋 시 자동 검증 (pre-commit)
bash scripts/validate-vault.sh            # OK가 나와야 정상
```

`install-hooks.sh`는 `core.hooksPath`를 `.githooks`로 바꾼다. 이후 규칙을 위반한
노트는 커밋 자체가 막힌다.

## 5. 반드시 고칠 곳 — 한 군데

`AGENTS.md` 12번째 줄의 사용자 정보를 본인 것으로 바꾼다.

```
- 사용자: <이름>, AIMEDBIO <직함>
```

그 외 규칙(문체, 약어, 태그 allowlist, 폴더 규칙)은 팀 공통이므로 그대로 둔다.

## 6. 팀 공통으로 유지할 것

다음은 팀원 간 vault 구조를 일치시키기 위한 공통 정본이다. 혼자 바꾸지 말고
바꿀 일이 생기면 팀에 공유해 양쪽 vault를 함께 갱신한다.

- `AGENTS.md` — 서술 규칙 정본 (`CLAUDE.md`, `GEMINI.md`가 이 파일의 symlink)
- `config/vault-schema.yaml` — 기계 판정 규칙 (폴더별 type, status 허용값, `known_tags`)
- `scripts/validate-vault.py` — 검증 엔진
- `Templates/` — 신규 노트 골격
- `index.md`, `Projects MOC.md`, `People MOC.md`, `Task Dashboard.md` — 골격만 제공, 내용은 각자 채운다

특히 `known_tags`는 allowlist다. 목록에 없는 태그를 쓰면 검증이 실패한다.
새 태그가 필요하면 임의로 추가하지 말고 팀에 먼저 공유한다.

## 7. 창 표시와 개인 설정

WSLg에서는 Tray의 **Hide on launch**, **Run in background** 기본값을 끈다.
설치 후 메인 창이 보여야 하며, 닫기 버튼은 일반 앱처럼 창을 닫는다.
Windows 트레이 연동과 전역 단축키 복원은 환경별로 다르므로 최초 실행을 이 기능에 의존하지 않는다.

### 개인 설정 (선택)

`.claude/settings.local.json.example`을 `.claude/settings.local.json`으로 복사해
본인 권한 설정으로 쓴다. 이 파일은 각자 로컬 설정이므로 팀에서 맞추지 않는다.

## 8. 첫 노트 만들어 보기

`Projects/` 폴더에 새 노트를 만들면 Templater가 `Templates/Project.md`를 자동 적용한다.
템플릿을 손으로 복사했다면 Templater token(각괄호와 퍼센트로 감싼 표현)을 전부
실제 값으로 치환해야 한다. 치환하지 않은 token이 남아 있으면 검증이 실패한다.

이메일은 subject를 직접 채워야 한다. 비어 있는 필수 입력을 자동으로 지어내지 않는다.
다음 8개 폴더 각각에서 실제 노트를 만들어 type/날짜/태그와 token 치환을 확인한다:
Daily, Projects, People, Organizations, Products, Meetings, Email_Drafts, References.
시험 파일도 폴더의 명명 규칙과 필수 필드를 충족시킨다.

작성 후:

```bash
bash scripts/validate-vault.sh
```
