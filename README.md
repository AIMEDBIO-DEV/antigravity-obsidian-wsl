# Antigravity + Obsidian on WSLg

Windows PC의 WSL Ubuntu에 **Antigravity 2.0과 Obsidian Linux 앱**을 설치하고,
같은 로컬 보관함의 Markdown 파일을 작성·열람하는 설치 도구입니다.
두 앱의 창은 WSLg를 통해 Windows 바탕화면에 표시됩니다.

기본 보관함은 **설치를 실행한 Linux 사용자의 `~/Obsidian/Notes`**입니다.
Windows 사용자 이름과 Linux 사용자 이름이 달라도 됩니다.
설치 코드, 바로가기, 시작 노트의 경로는 실행 시 현재 사용자 홈으로 생성됩니다.

## 지원 범위

- Windows 11 또는 Windows 10 build 19044 이상, WSL2 + WSLg
- **x64 PC**, Ubuntu 22.04 이상 권장
- 이 구성의 실제 앱 동작 검증: Ubuntu 26.04 / WSLg 1.0.71
- ARM64, 일반 Linux 데스크톱, 원격/네트워크 보관함은 이번 배포의 검증 범위에 포함되지 않습니다.
- Antigravity 로그인에 사용할 본인 계정이 필요합니다. 기업 계정은 조직의 제품 이용 권한이 필요합니다.

## 설치 흐름과 역할

**선행 준비 → 저장소 내려받기 → Antigravity CLI에 설치 요청 → 앱 로그인 및 보관함 연결** 순서로 진행합니다.

| 구분 | 담당 범위 |
| --- | --- |
| 사용자 선행 작업 | WSL2/WSLg Ubuntu 설치, Antigravity CLI 설치·로그인, GitHub 저장소 접근 준비 |
| 이 저장소 | Antigravity 2.0 **데스크톱 앱**, Obsidian, 필요한 라이브러리·글꼴·바로가기·로컬 보관함 설치 |
| 설치 후 사용자 작업 | 데스크톱 앱 로그인, 프로젝트 폴더 선택, 노트 작성 확인 |

**WSL과 Antigravity CLI 자체의 설치·계정 설정은 이 저장소의 자동화 범위 밖입니다.**
아래 선행 작업은 새 PC 사용자를 위한 안내입니다.
CLI(`agy`)는 설치 과정을 진행할 도구이며, 이 저장소가 설치하는 Antigravity 데스크톱 앱과 별개입니다.
스크립트를 직접 실행할 경우 CLI는 필요하지 않습니다.

## 1. 선행 작업: Windows에서 WSL 준비

이미 WSLg Ubuntu를 사용한다면 다음 단계로 진행합니다.
처음 설치하는 PC는 관리자 PowerShell에서 실행한 뒤 안내에 따라 재부팅합니다.

```powershell
wsl --install -d Ubuntu
```

Ubuntu를 열어 Linux 사용자 이름과 암호를 정합니다. Windows 사용자 이름과 같을 필요는 없습니다.
기존 설치의 상태는 PowerShell에서 확인합니다.

```powershell
wsl --version
wsl --list --verbose
```

WSLg가 없거나 오래된 경우 `wsl --update` 후 WSL을 재시작합니다.
`wsl --shutdown`은 모든 WSL 작업을 종료하므로 작업을 저장한 후 실행하세요.

## 2. 선행 작업: Ubuntu에 Antigravity CLI 설치·로그인

WSL Ubuntu 터미널에서 필요한 기본 도구와 CLI를 설치합니다.
CLI를 특정 프로젝트 폴더에 설치할 필요는 없습니다.
공식 설치기는 현재 Linux 사용자의 `~/.local/bin/agy`에 실행 파일을 설치합니다.

```bash
sudo apt update
sudo apt install -y curl ca-certificates git
curl -fsSL https://antigravity.google/cli/install.sh | bash
~/.local/bin/agy
```

CLI 안내에 따라 본인의 계정으로 로그인합니다.
브라우저가 자동으로 열리지 않으면 CLI에 표시되는 인증 안내를 따릅니다.
로그인을 마치면 CLI를 종료하고 아래 저장소 폴더에서 다시 실행합니다.
CLI는 일반 Linux 사용자로 실행하며 `sudo`를 붙이지 않습니다.

설치·인증 방식의 최신 내용은 [Antigravity CLI 공식 안내](https://antigravity.google/docs/cli/install/)를 참고하세요.

## 3. 저장소 내려받기

이 저장소가 비공개이면 AIMEDBIO-DEV 저장소 접근 권한이 필요합니다.
Git 인증을 설정하거나 GitHub에서 **Code → Download ZIP**으로 내려받아 Ubuntu의 홈 아래에 압축을 풉니다.
Windows에 로그인된 GitHub 계정이 Ubuntu Git에 자동으로 적용되지는 않습니다.

```bash
mkdir -p ~/apps
cd ~/apps
git clone https://github.com/AIMEDBIO-DEV/antigravity-obsidian-wsl.git
cd antigravity-obsidian-wsl
```

**Antigravity 계정 로그인과 GitHub 인증은 별개입니다.**
비공개 저장소의 경우 해당 GitHub 계정에 저장소 접근 권한이 있어야 합니다.
Git 인증 준비가 어렵다면 GitHub 웹에서 ZIP으로 내려받아 Ubuntu 홈 아래에 압축을 푸는 방법을 사용하세요.

## 4. Antigravity CLI에 설치 요청

내려받은 저장소 폴더에서 CLI를 실행합니다. ZIP으로 받은 경우에도 압축을 푼 저장소 폴더로 이동합니다.

```bash
~/.local/bin/agy
```

다음 요청을 붙여넣습니다.

```text
이 저장소의 README를 읽고 현재 WSL 환경에 Antigravity 데스크톱 앱과 Obsidian을 설치해 줘.
WSL과 Antigravity CLI는 이미 설치되어 있어.
현재 Linux 사용자의 홈 경로를 사용하고 기존 노트와 설정은 보존해 줘.
먼저 ./install.sh --plan으로 설치 경로를 확인하고,
./scripts/install-deps.sh와 ./install.sh를 실행해 줘.
설치 후 python3 scripts/doctor.py로 점검하고 두 앱 실행까지 확인해 줘.
sudo 암호 입력, 계정 로그인, GUI 폴더 선택이 필요하면 내가 직접 진행할 수 있게 안내해 줘.
```

`sudo` 암호는 터미널의 암호 입력란에 입력합니다. CLI 대화에 암호를 적을 필요는 없습니다.
설치 후 데스크톱 앱 로그인과 보관함 선택은 아래 최초 연결 절차를 따릅니다.

### CLI 없이 직접 설치하는 방법

같은 저장소 폴더에서 다음 스크립트를 직접 실행해도 됩니다.

```bash
# 경로와 버전 확인만 수행
./install.sh --plan

# 시스템 라이브러리, 한글/이모지 글꼴 설치 (sudo 암호 필요)
./scripts/install-deps.sh

# 앱과 보관함은 일반 Linux 사용자로 설치
./install.sh
```

ZIP으로 받았고 실행 권한이 없다면 먼저 실행합니다.

```bash
chmod +x install.sh scripts/install-deps.sh
```

다른 로컬 보관함 경로를 사용하려면:

```bash
./install.sh --vault "$HOME/Obsidian/Research Notes"
```

`sudo ./install.sh`로 실행하지 마세요. 설치기는 root 실행을 거부합니다.
설치된 두 앱을 자동 실행하거나 로그인을 대신 수행하지는 않습니다.

## 5. 앱 실행과 최초 연결

Linux 시작 메뉴 항목은 설치 시 등록되지만, WSLg가 이를 Windows 시작 메뉴에 자동으로 표시하지 않는 환경도 있습니다.
**Windows 바탕화면과 시작 메뉴에 확실하게 등록하려면** 설치 후 Ubuntu의 저장소 폴더에서 실행합니다.

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$(wslpath -w "$PWD/scripts/create-windows-shortcuts.ps1")" -Distribution "$WSL_DISTRO_NAME"
```

이 명령은 **Antigravity (WSL)**과 **Obsidian (WSL)** 바로가기를 Windows 바탕화면 및
시작 메뉴의 **WSL Notes** 폴더에 만듭니다. Windows 사용자명, OneDrive 바탕화면 위치,
해당 WSL 배포판의 기본 Linux 사용자·홈 경로를 자동으로 확인합니다.
Antigravity만 만들려면 명령 뒤에 `-App antigravity`를 추가합니다.
기존 같은 이름의 바로가기 대상이 다르면 백업을 만든 뒤 갱신합니다.
바로가기는 `wsl.exe`를 사용하며, 등록 전에 임시 바로가기로 Linux 명령의 실제 실행을 검사합니다.
이 바로가기 도구에서는 배포판·Linux 사용자 이름에 공백이 없어야 합니다(예: `Ubuntu`, `Ubuntu-24.04`).
`WSL_E_DISTRO_NOT_FOUND`가 표시되는 이전 바로가기는 위 등록 명령을 다시 실행해 갱신하세요.
일부 WSL 버전은 바로가기의 배포판·사용자 이름에 붙인 따옴표를 이름의 일부로 처리하므로,
등록 도구는 해당 인수에 불필요한 따옴표를 넣지 않습니다.

바로가기를 더블클릭하면 WSLg 앱이 실행됩니다. WSLg를 별도로 시작할 필요는 없습니다.
다중 모니터에서 최대화 후 커서 좌표가 어긋나면, 최대화를 해제하고 **F11 전체화면**을 사용해 보세요.
검증한 PC에서는 F11 전환이 정상 동작했습니다.

Ubuntu 터미널에서 직접 실행할 수도 있습니다.

```bash
~/.local/bin/antigravity-wsl
~/.local/bin/obsidian-wsl
```

1. Obsidian에서 `Notes` 보관함과 `시작하기` 노트를 확인합니다.
   설치 중 Obsidian이 실행 중이었다면 **Open folder as vault**로 설치 완료 메시지의 경로를 직접 선택합니다.
2. Antigravity에서 본인의 개인/기업 계정으로 로그인합니다.
3. 왼쪽 **Create New Project → New Project**를 선택합니다.
4. 폴더 선택 창에서 **Ctrl+L**을 누르고 설치 결과의 **절대 경로**를 입력합니다.
   Ubuntu에서 `realpath ~/Obsidian/Notes`로 복사할 경로를 확인할 수 있습니다.
   `~`나 `$HOME`을 GUI에 그대로 붙여넣지 마세요.
5. **Open**으로 폴더를 선택하고 **Local** 환경에서 대화를 시작합니다.

예시 요청:

```text
이 프로젝트는 로컬 Obsidian 보관함이야.
Inbox/첫 메모.md를 한국어 Markdown으로 작성해 줘.
내용은 이번 주 업무 정리 방법이고, [[시작하기]] 링크를 포함해 줘.
실제 파일로 저장해 줘. 기존 노트와 .obsidian 설정은 변경하지 마.
```

Obsidian에서 `Inbox/첫 메모.md`가 나타나는지 확인합니다.
같은 폴더를 사용하는 방식이므로 노트 작성에 별도 MCP나 동기화 플러그인은 필요하지 않습니다.
동일 노트를 두 앱에서 동시에 수정하면 편집 충돌이 생길 수 있습니다.

## 설치되는 항목

| 항목 | 위치 |
| --- | --- |
| 앱 버전별 파일 | `~/.local/share/wsl-notes/apps/` |
| 실행 명령 | `~/.local/bin/antigravity-wsl`, `~/.local/bin/obsidian-wsl` |
| 앱 전용 URL 도우미 | `~/.local/share/wsl-notes/bin/xdg-open` |
| Linux 시작 메뉴 항목 | `~/.local/share/applications/*-wsl.desktop` |
| 다운로드 캐시 | `~/.cache/wsl-notes/` |
| 설치 기록 | `~/.local/share/wsl-notes/install.json` |
| 기본 보관함 | `~/Obsidian/Notes` |

앱 바이너리는 저장소에 포함하지 않고 공식 Google/Obsidian 배포처에서 내려받습니다.
[versions.json](versions.json)의 버전과 SHA-256을 확인한 뒤 설치합니다.
해시는 검증에 사용한 배포 파일의 해시이며, 공급업체 서명을 대신하지 않습니다.
현재 고정 버전은 Antigravity **2.12.2**, Obsidian **1.13.7**입니다.

설치기는 기존 노트와 보관함 설정을 덮어쓰지 않습니다.
Obsidian의 보관함 목록에 새 경로를 추가할 때 기존 목록을 유지하고 원본 JSON을 백업합니다.
기존 사용자 인증이나 MCP 설정을 가져오는 작업은 하지 않습니다.
앱 자체가 최초 실행 시 이전 제품 설정을 마이그레이션할 수는 있습니다.

URL 도우미는 이 설치의 앱에만 적용하며 시스템 `xdg-open`을 바꾸지 않습니다.
HTTP/HTTPS 로그인 링크는 Windows 기본 브라우저로 엽니다.
Windows의 `antigravity://` 연결 설정은 변경하지 않습니다.

## 점검 및 문제 해결

```bash
python3 scripts/doctor.py
```

- **기존 실행 파일 충돌:** 설치기가 만들지 않은 동일 이름의 launcher는 덮어쓰지 않습니다.
  표시된 기존 파일을 확인하고 별도 이름으로 백업한 뒤 재시도하세요.
- **라이브러리 누락:** `./scripts/install-deps.sh`를 실행한 뒤 다시 설치합니다.
- **한글이 네모로 표시:** 의존성 설치 후 두 앱을 종료하고 다시 실행합니다.
  한글 표시용 글꼴 설치와 한글 키보드 입력기 설정은 별개입니다. 한글 입력은 Windows/WSLg 환경에 따라 추가 IME 설정이 필요할 수 있습니다.
- **검은 화면/Wayland 문제:** 일회성으로 `~/.local/bin/antigravity-wsl --ozone-platform=x11`을 시도합니다.
- **sandbox 오류:** root로 실행하지 마세요. `--no-sandbox`를 기본 실행 옵션으로 추가하지 않습니다.
  배포판의 AppArmor/user namespace 정책은 관리자와 확인하세요.
- **로그인 대기:** 브라우저 로그인 후 Linux 앱으로 돌아오는지 확인합니다.
  Windows 앱이 대신 열리면 브라우저에 표시된 수동 인증 방법을 사용합니다.
- **MCP Error:** 노트 파일 작성에 MCP는 필요하지 않습니다. 기존 MCP 오류는 별도로 진단합니다.
- **프로젝트 폴더 선택:** GUI에서 사용자가 직접 선택합니다. 화면 좌표를 이용한 자동 입력은 하지 않습니다.

상세 앱 로그는 `~/.config/Antigravity/logs/`에서 확인할 수 있습니다.
로그에 인증 관련 값이 포함될 수 있으므로 원문을 저장소에 올리지 마세요.

## 재설치·업데이트·제거

같은 버전으로 다시 실행해도 기존 노트는 유지됩니다.
캐시를 미리 받은 환경에서는 `./install.sh --offline`을 사용할 수 있습니다.
버전 업데이트는 유지보수자가 공식 URL/해시를 갱신하고 검증한 저장소 버전을 받아 다시 설치합니다.
앱 자체의 자동 업데이트 동작은 제품에 따라 다르므로 설치 기록과 실제 앱 버전은 달라질 수 있습니다.

제거하려면 두 앱을 종료하고 위 표의 앱 파일, 실행 명령, 시작 메뉴 항목을 삭제합니다.
**`~/Obsidian/Notes` 및 앱 사용자 설정은 별도 데이터이므로 보존하세요.**
이 도구는 노트 삭제 명령을 제공하지 않습니다.

## 개발 및 검증

```bash
python3 -m unittest discover -s tests -v
bash -n install.sh scripts/install-deps.sh
```

테스트는 임시 사용자 홈에서 경로의 공백·특수문자, 재실행, 기존 노트/설정 보존,
다운로드 해시 검사와 압축 경로 검사를 확인합니다. 실제 GUI 로그인·노트 생성은 WSLg PC에서 별도로 확인합니다.

## 참고

- [Antigravity 공식 다운로드](https://antigravity.google/download?platform=linux)
- [Obsidian 공식 다운로드](https://obsidian.md/download)
- [Microsoft WSL GUI 앱 안내](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)

Antigravity와 Obsidian은 각 공급업체가 배포하는 별도 제품이며 해당 이용 조건이 적용됩니다.
이 저장소는 두 제품의 공식 설치 도구가 아닙니다.
