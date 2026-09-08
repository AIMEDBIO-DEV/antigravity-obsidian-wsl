# WSL Notes 설치 작업 지침

사용자가 이 저장소로 설치를 요청하면 README.md를 읽고 **실제 사용 확인까지 같은 작업으로 진행**한다.
스크립트 개발이나 코드 리뷰 요청에는 설치를 실행하지 않는다.

## 설치 요청의 완료 범위

1. WSL2/WSLg, x64 Ubuntu, 일반 Linux 사용자, GitHub 접근 준비를 확인한다.
2. `./setup.sh --plan`으로 사용자별 경로와 단계를 확인한다.
3. 팀 규칙 번들까지 요청받으면 `./setup.sh --profile cmc`를 실행한다. 일반 빈 보관함은 `./setup.sh --profile minimal`을 사용한다. 이 명령이 의존성, 앱, 입력기, 보관함, Windows 숨김 바로가기,
   doctor 점검, 입력 엔진 검증, 두 앱 실행 요청을 순서대로 수행한다.
   sudo 암호는 사용자가 터미널에서 직접 입력하도록 한다. 대화로 암호를 받지 않는다.
4. 자동 단계가 성공해도 여기서 설치 완료로 종료하지 않는다. 로그인·프로젝트 연결·사용 검증을 이어간다.
   계정 로그인은 사용자가 수행해야 한다. 로그인 완료 후 같은 대화에서 계속한다.
5. `~/.local/share/wsl-notes/install.json`의 `vault` 절대 경로를 읽는다.
   Antigravity에서 Create New Project → New Project로 그 폴더를 선택하고 **Local** 모드로 연결한다.
   GUI 도구가 있으면 화면/요소를 확인하고 지원되는 UI로 진행한다.
   GUI 도구가 없으면 한 단계씩 사용자에게 안내하고 확인을 받아 계속한다.
   추측한 좌표, 비공개 내부 API, 사용자 설정 파일 강제 편집으로 연결 성공을 가정하지 않는다.
6. Obsidian에서 같은 보관함이 열린 것을 확인한다. 자동 열기가 실패하면 Open folder as vault를 안내한다.
7. 사용자가 실제 앱에서 한/영 키 또는 Shift+Space로 한글을 입력하도록 확인한다.
   입력 엔진 테스트 통과만으로 물리 키보드 검증 완료라고 하지 않는다.
8. Antigravity **데스크톱 앱**에 사용하지 않은 시험 노트 생성을 요청한다. install.json의 test_note_folder를 사용한다(CMC는 References, minimal은 Inbox). CMC에서는 type: reference와 실제 본문을 포함하고 보관함 AGENTS.md/스키마를 따른다.
   파일이 UTF-8 한글로 생성됐는지 읽고, Obsidian에서 열리는지 확인한다.
   CLI가 대신 노트를 만들어 데스크톱 앱의 작성 성공으로 보고하지 않는다.

## 재개와 완료 보고

- 설치 이후 단계만 실패했으면 원인을 해결하고 `./setup.sh --finish-only`로 재개한다.
  이 옵션은 기존 install.json의 보관함을 사용한다.
- 자동 단계 결과는 `~/.local/share/wsl-notes/setup-status.json`에 기록된다.
  `launch_requested`는 UI 표시 확인이 아니다. `user_checks_pending`은 사용자/UI 검증이 남았다는 뜻이다.
- 각 사용자/UI 검증을 실제로 마친 뒤에만 해당 항목을 pending에서 제거하고,
  `verified_checks` 객체에 검증 방법(사용자 확인/실제 파일 경로 등)을 기록한다.
  인증 토큰이나 비밀번호는 기록하지 않는다.
- 마지막 보고에는 바로가기, 앱 실행, 로그인/Local 프로젝트, 물리 한글 입력,
  노트 작성→Obsidian 열람 각각의 완료 여부를 명시한다. 남은 항목이 있으면 전체 완료라고 하지 않는다.
- 기존 노트·인증·MCP 설정을 보존한다. CLI Remote Control 등록은 설치 범위가 아니다.

## 보관함 규칙 템플릿

- 사용자가 팀 규칙/번들 포함 설치를 요청하면 cmc 프로필을 같은 설치 작업에 포함한다. 번들 요청이 없는 일반 설치에는 강제로 적용하지 않는다.
- 적용을 요청받으면 `vault-templates/README.md`를 읽고 `python3 scripts/vault.py`를 사용한다.
  기존 노트를 덮어쓰거나 옮기지 않으며, `--adopt-starter-note`는 사용자가 요청할 때만 붙인다.
- 규칙 파일(`vault-templates/*/config/vault-schema.yaml`, `vault-templates/*/AGENTS.md`,
  `vault-templates/addons.json`)은 팀 공통 정본이므로 이 작업에서 수정하지 않고 문제만 보고한다.
- CMC 첫 실행에서 플러그인 신뢰 화면을 안내하고, Settings → Templater → Trigger Templater on new file creation을 각 PC에서 허용하도록 안내한다.
  GUI 도구가 있으면 실제 화면을 확인하며 진행하고, 없으면 사용자의 확인을 받아 계속한다. local storage를 직접 덮어써 허용을 우회하지 않는다.
- 8개 폴더와 Daily 버튼으로 자동 적용을 확인한다. cursor token이 남거나 빈 노트가 생기면 완료가 아니다.
  Email_Drafts의 subject는 사용자 입력을 받아 채운다. 생성 후 보관함의 `bash scripts/validate-vault.sh`를 실행한다.
- `setup-status.json`의 community_plugins, templater_device_trigger, folder_templates, daily_template,
  window_visible 항목을 실제 확인한 경우만 완료 기록한다. IBus 엔진 테스트를 물리 키보드 검증으로 대체하지 않는다.
- 프로필 재개는 `./setup.sh --finish-only`다. 저장된 CMC 경로와 SETUP.md를 사용한다.
- 적용 완료는 규칙 검증과 실제 Obsidian 템플릿 시험을 모두 통과한 뒤에만 보고한다.
