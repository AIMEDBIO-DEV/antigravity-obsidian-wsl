# CMC 번들 보완 검증 (2026-09-08)

WSL Ubuntu에서 Obsidian 1.13.7과 고정된 Templater 2.25.0을 사용했다.
실사용 보관함 대신 `/tmp/wsl-notes-cmc-fixed-gui/CMC`와 별도 Electron 사용자 데이터 경로를 사용했다.
앱 설치 전체를 다시 실행하지 않고, 설치기의 `create_profile_vault` 경로로 번들을 적용했다.

## 수정과 결과

- 8개 템플릿의 cursor token을 제거했다. 실제 Obsidian Vault API로 각 폴더에 빈 파일을 만들고 열어 Templater가 처리하도록 했다. 8개 모두 title/date/type이 적용되고 미처리 token이 없었다.
- References 폴더의 실제 New note 메뉴로도 자동 적용을 확인했다.
- 실제 Daily 리본 버튼으로 오늘의 노트를 생성했다. type/date가 적용되고 템플릿 중복이 없었다.
- Templater의 Trigger Templater on new file creation은 기기별 설정이다. 설정 UI에서 경고 확인란과 Enable 버튼을 눌렀으며 local storage 직접 쓰기는 하지 않았다. 앱 재시작 후 허용 상태가 유지됐다.
- Tray의 hideOnLaunch/runInBackground를 false로 바꿨다. 최초 실행과 재시작 모두 메인 창이 표시됐다. 트레이 아이콘 자체의 Windows 통합은 완료 조건으로 삼지 않는다.
- Email의 필수 subject에 시험 값을 채운 뒤 `validate-vault.sh`가 18개 markdown 파일을 통과했다. subject는 업무별 입력값이므로 자동 생성하지 않는다.
- `setup.sh --profile cmc`가 번들 적용과 CMC 경로 등록, SETUP.md 열기 및 기기별 확인 목록까지 연결되도록 했다. 기존 minimal 설치와 프로필 재개는 단위 테스트로 검증했다.
- 자동 테스트 31개, 셸 문법 검사, CMC plan 및 diff 공백 검사가 통과했다.

## 다른 PC에서 남는 확인

새 PC의 WSL 설치부터 agy CLI 로그인, Windows Antigravity 설치까지 전체 재설치는 이번 검증 범위가 아니다.
실제 물리 한/영 키, Antigravity WSL 연결·보관함 열기와 노트 작성 왕복은 해당 PC에서 확인해야 한다.
입력기 코드는 이번 보완에서 변경하지 않았다. 합성 키 입력은 물리 키보드 검증으로 대체하지 않는다.

`./setup.sh --profile cmc` 이후 AGENTS.md와 보관함 SETUP.md에 따라 플러그인 신뢰,
Templater 기기별 허용, 폴더/Daily 생성, 한글 입력, 앱 간 노트 왕복까지 이어서 확인한다.
`setup-status.json`의 pending 항목은 실제 확인한 것만 제거한다.

기존 보관함에서 새 노트 위치가 맞지 않거나 이전 cursor 템플릿/Tray 숨김 설정이 발견되면 적용은 중단한다.
기존 파일을 자동으로 덮어쓰지 않으며, 백업 후 안내에 따라 설정과 템플릿을 갱신한다.
