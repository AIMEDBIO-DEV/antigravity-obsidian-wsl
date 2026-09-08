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

## 2. vault 배치

이 폴더를 그대로 vault 위치로 옮기고 git 저장소로 만든다.

```bash
mv vault-starter-kit ~/Obsidian
cd ~/Obsidian
git init
```

`CLAUDE.md`, `GEMINI.md`, `.agents/skills`는 symlink다. 검증기가 symlink 여부를
실제로 확인하므로 Windows에서 zip으로 풀었다면 다음으로 다시 만든다.

```bash
rm -f CLAUDE.md GEMINI.md .agents/skills
ln -s AGENTS.md CLAUDE.md
ln -s AGENTS.md GEMINI.md
ln -s ../.claude/skills .agents/skills
```

## 3. Obsidian에서 vault 열기

Obsidian → "Open folder as vault" → 위 폴더 선택.
`.obsidian/`이 이미 들어 있으므로 다음이 그대로 적용된다.

- Minimal 테마 + Minimal Settings
- Templater (folder 단위 자동 템플릿), core Templates는 꺼진 상태
- Daily notes 폴더 `Daily/`, 형식 `YYYY-MM-DD`
- 검색 제외 경로: `Templates/`, `scripts/`, `config/`

플러그인 파일이 포함되어 있지만, Obsidian이 업데이트를 안내하면 커뮤니티 스토어에서
갱신해도 된다. 단 Templater 설정은 아래 조건을 유지해야 검증을 통과한다.

- `templates_folder` = `Templates`
- trigger mode = folder mapping
- folder mapping 8개가 `config/vault-schema.yaml`의 `note_folders`와 정확히 1:1
- system command / user script 경로는 비워 둔다

## 4. 검증 환경

```bash
pip install -r scripts/requirements.txt   # PyYAML만 필요
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

## 7. 개인 설정 (선택)

`.claude/settings.local.json.example`을 `.claude/settings.local.json`으로 복사해
본인 권한 설정으로 쓴다. 이 파일은 각자 로컬 설정이므로 팀에서 맞추지 않는다.

## 8. 첫 노트 만들어 보기

`Projects/` 폴더에 새 노트를 만들면 Templater가 `Templates/Project.md`를 자동 적용한다.
템플릿을 손으로 복사했다면 Templater token(각괄호와 퍼센트로 감싼 표현)을 전부
실제 값으로 치환해야 한다. 치환하지 않은 token이 남아 있으면 검증이 실패한다.

작성 후:

```bash
bash scripts/validate-vault.sh
```
