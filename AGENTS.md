# WSL Notes 설치 작업 지침

사용자가 이 저장소로 설치를 요청하면 README.md를 읽고 **실제 사용 확인까지 같은 작업으로 진행**한다.
스크립트 개발이나 코드 리뷰 요청에는 설치를 실행하지 않는다.

## 설치 요청의 완료 범위

1. WSL2/WSLg, x64 Ubuntu, 일반 Linux 사용자, GitHub 접근 준비를 확인한다.
   Windows용 Antigravity 2.0은 사용자가 직접 설치해 둔 것으로 본다. 이 저장소는 설치하지 않으며 설치 흐름도 안내하지 않는다.
2. `./setup.sh --plan`으로 사용자별 경로와 단계를 확인한다.
3. 팀 규칙 번들까지 요청받으면 `./setup.sh --profile cmc`를 실행한다. 일반 빈 보관함은 `./setup.sh --profile minimal`을 사용한다. 이 명령이 의존성, Obsidian, 입력기, 보관함, Windows 숨김 바로가기(Obsidian),
   officecli·Node/pnpm·open-slide 작업공간(`~/Slides`)과 cmc-weekly 테마 설치, doctor 점검, 입력 엔진 검증, Obsidian 실행 요청을 순서대로 수행한다.
   사용자가 도구를 원하지 않으면 `--no-tools`를 붙인다.
   sudo 암호는 사용자가 터미널에서 직접 입력하도록 한다. 대화로 암호를 받지 않는다.
4. 자동 단계가 성공해도 여기서 설치 완료로 종료하지 않는다. Antigravity 연결·보관함 열기·사용 검증을 이어간다.
   Antigravity 로그인과 WSL 연결은 사용자가 수행해야 한다. 완료 후 같은 대화에서 계속한다.
5. `~/.local/share/wsl-notes/install.json`의 `vault` 절대 경로를 읽는다.
   Windows의 Antigravity 2.0에서 **Windows Subsystem for Linux** 기능으로 이 배포판(`$WSL_DISTRO_NAME`)에 연결하게 한다.
   연결하면 앱이 그 배포판으로 다시 시작된다. 그 상태에서 `vault` 경로(Linux 절대 경로)를 프로젝트 폴더로 열게 한다.
   GUI 도구가 있으면 화면/요소를 확인하고 지원되는 UI로 진행한다.
   GUI 도구가 없으면 한 단계씩 사용자에게 안내하고 확인을 받아 계속한다.
   세부 클릭 순서를 추측해 단정하지 않는다. 추측한 좌표, 비공개 내부 API, 사용자 설정 파일 강제 편집으로 연결 성공을 가정하지 않는다.
   연결됐는지는 사용자가 앱에서 WSL 환경으로 표시되는 것을 확인하고 보관함 파일이 보이는 것으로 판단한다.
6. Obsidian(WSLg)에서 같은 보관함이 열린 것을 확인한다. 자동 열기가 실패하면 Open folder as vault를 안내한다.
7. 사용자가 실제 **Obsidian**에서 한/영 키 또는 Shift+Space로 한글을 입력하도록 확인한다.
   입력 엔진 테스트 통과만으로 물리 키보드 검증 완료라고 하지 않는다. IBus는 Obsidian(WSLg)용이며 Windows의 Antigravity에는 적용되지 않는다.
8. WSL에 연결된 Antigravity **데스크톱 앱**에 사용하지 않은 시험 노트 생성을 요청한다. install.json의 test_note_folder를 사용한다(CMC는 References, minimal은 Inbox). CMC에서는 type: reference와 실제 본문을 포함하고 보관함 AGENTS.md/스키마를 따른다.
   파일이 UTF-8 한글로 생성됐는지 읽고, Obsidian에서 열리는지 확인한다.
   CLI가 대신 노트를 만들어 데스크톱 앱의 작성 성공으로 보고하지 않는다. WSL에 연결되지 않은 Antigravity의 결과는 인정하지 않는다.

9. `~/.local/share/wsl-notes/tools-install.json`이 있고 `complete`가 true이면 도구도 실제로 확인한다.
   - **officecli:** 사용하지 않은 임시 경로(예: `/tmp`)에 `officecli create`로 docx를 만들고 파일이 생성됐는지 읽는다. 사용자의 기존 문서를 시험에 쓰지 않는다.
   - **open-slide:** `~/.local/bin/slides-wsl`로 개발 서버를 띄우고 사용자가 Windows 브라우저에서 화면을 보는지 확인받는다. Themes 패널의 `cmc-weekly` 데모 표시까지 안내한다.
   - **슬라이드 작성:** 사용자가 원하면 Antigravity 데스크톱 앱이나 `~/Slides`의 CLI로 `/create-slide` 시험 덱을 만들고 미리보기에서 열리는지 확인한다.
   CLI가 대신 실행해 놓고 화면 확인을 마친 것으로 보고하지 않는다.

## 재개와 완료 보고

- `user_checks_pending`의 Antigravity 항목은 `antigravity_wsl_connect`(로그인·WSL 연결)와 `antigravity_vault_open`(보관함 열기)이다.
- 설치 이후 단계만 실패했으면 원인을 해결하고 `./setup.sh --finish-only`로 재개한다.
  이 옵션은 기존 install.json의 보관함을 사용한다.
- 자동 단계 결과는 `~/.local/share/wsl-notes/setup-status.json`에 기록된다.
  `launch_requested`는 UI 표시 확인이 아니다. `user_checks_pending`은 사용자/UI 검증이 남았다는 뜻이다.
- 각 사용자/UI 검증을 실제로 마친 뒤에만 해당 항목을 pending에서 제거하고,
  `verified_checks` 객체에 검증 방법(사용자 확인/실제 파일 경로 등)을 기록한다.
  인증 토큰이나 비밀번호는 기록하지 않는다.
- 마지막 보고에는 Obsidian 바로가기·실행, Antigravity WSL 연결·보관함 열기, Obsidian 물리 한글 입력,
  노트 작성→Obsidian 열람 각각의 완료 여부를 명시한다. 남은 항목이 있으면 전체 완료라고 하지 않는다.
- `tools-install.json`의 `complete`가 false이거나 `--offline`으로 단계가 생략됐으면 도구 항목을 완료라고 하지 않는다. 네트워크 연결 후 `python3 scripts/tools.py`로 재개한다.
- 도구 항목(`officecli_smoke`, `open_slide_preview`, `cmc_weekly_theme`)도 `verified_checks`에 검증 방법을 기록한 뒤에만 pending에서 제거한다.
- officecli(공식 스크립트, 자동 업데이트)와 open-slide(`@latest`)는 버전이 고정되지 않는다. 설치된 버전을 보고서에 적고 이 점을 숨기지 않는다.
- 기존 노트·인증·MCP 설정을 보존한다. CLI Remote Control 등록은 설치 범위가 아니다.

## 슬라이드 테마 번들

- `slide-templates/*`와 `~/Slides`의 기존 테마·슬라이드는 이 작업에서 수정하지 않고 문제만 보고한다. 설치기는 없는 파일만 복사한다.
- 번들의 데모에는 가상의 예시 데이터만 둔다. 실명·협력사명·과제 코드·실제 진행 상황·원본 pptx를 넣지 않는다(공개 저장소).
- `~/Slides`가 open-slide 작업공간이 아니면 수정하지 말고 사용자에게 다른 경로(`--slides`)를 묻는다.

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
