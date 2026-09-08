# 보관함 규칙 템플릿

설치기가 만드는 기본 보관함(`~/Obsidian/Notes`)은 폴더 3개와 시작 노트만 있는 빈 상태입니다.
이 폴더의 템플릿은 그 위에 **팀에서 쓰는 노트 작성 규칙**을 얹습니다.
규칙에는 폴더별 노트 종류, frontmatter 필수 항목, 태그 allowlist, 검증 스크립트가 들어 있습니다.

적용은 선택 사항입니다. `setup.sh`와 `install.sh`의 동작은 이 템플릿과 무관합니다.

## 템플릿 목록

| 이름 | 용도 |
| --- | --- |
| `cmc` | AIMEDBIO CMC팀 보관함 규칙 (OKF v0.2 hard conformance + 팀 vault 규칙) |

## 적용 방법

```bash
# 변경 없이 대상 경로와 단계 확인
python3 scripts/vault.py --plan

# 기본 경로(~/Obsidian/CMC)에 적용하고 검증까지 실행
python3 scripts/vault.py --validate

# 설치기의 기본 보관함에 얹는 경우
python3 scripts/vault.py --vault "$HOME/Obsidian/Notes" --adopt-starter-note --validate
```

검증에는 PyYAML이 필요합니다.

```bash
pip install -r "$HOME/Obsidian/CMC/scripts/requirements.txt"
bash "$HOME/Obsidian/CMC/scripts/validate-vault.sh"
```

적용 후 할 일은 보관함에 복사되는 `SETUP.md`에 있습니다.

## 적용기의 동작 범위

- 없는 파일만 씁니다. 이미 있는 노트·설정 파일은 내용이 달라도 덮어쓰지 않고 목록으로 보고합니다.
- `CLAUDE.md`, `GEMINI.md`, `.agents/skills` symlink를 만듭니다. 규칙 정본은 `AGENTS.md` 하나입니다.
- `addons.json`에 고정한 플러그인·테마 파일을 공식 release에서 내려받아 SHA-256을 확인한 뒤 설치합니다.
  이미 있는 파일은 해시가 달라도 교체하지 않습니다. Obsidian이 설치한 플러그인 번들 끝에
  `/* nosourcemap */` 18바이트를 덧붙이기 때문에, 설치된 파일의 해시는 release 해시와 다를 수 있습니다.
- `--adopt-starter-note`를 주면 설치기가 만든 `시작하기.md`를 `References/`로 옮기고 frontmatter를 붙입니다.
  사용자가 편집한 노트는 옮기지 않고 중단합니다.
- 노트를 지우거나 기존 태그·상태를 바꾸지 않습니다.

## 저장소에 넣지 않는 파일

앱 바이너리를 저장소에 넣지 않는 기존 정책을 그대로 따릅니다.
플러그인·테마의 대용량 생성 번들(`main.js`, `theme.css`)은 템플릿에 포함하지 않고
`addons.json`의 공식 URL과 SHA-256으로 받습니다.
템플릿에는 `manifest.json`, `data.json`, 소형 `styles.css`만 들어 있습니다.

`addons.json`은 `versions.json`과 분리되어 있습니다.
`versions.json`은 `install.py`가 설치하고 launcher를 만드는 앱 목록이므로 다른 항목을 넣으면 안 됩니다.

## 템플릿 갱신

`cmc` 템플릿은 팀 공통 정본입니다. 규칙을 바꾸면 팀원 보관함도 함께 갱신해야 하므로
`config/vault-schema.yaml`의 태그·상태 목록과 `AGENTS.md`는 팀에 공유한 뒤 수정합니다.

플러그인 버전을 올릴 때는 `addons.json`의 URL·SHA-256과
`vault-templates/cmc/.obsidian/plugins/<id>/manifest.json`의 버전을 같이 맞춥니다.
`tests/test_vault_template.py`가 두 값의 일치를 검사합니다.
