# Antigravity (WSL 연결) + Obsidian on WSLg

Windows PC의 WSL Ubuntu에 **Obsidian Linux 앱**과 로컬 보관함을 설치하고,
**Windows용 Antigravity 2.0의 Windows Subsystem for Linux 연결 기능**으로 같은 보관함의 Markdown 파일을 작성하게 하는 설치 도구입니다.
Obsidian 창은 WSLg를 통해 Windows 바탕화면에 표시됩니다. Antigravity는 WSLg로 띄우지 않습니다.
함께 문서·슬라이드 도구인 **officecli**(Word/Excel/PowerPoint)와 **open-slide**(에이전트용 슬라이드 프레임워크),
팀 테마 `cmc-weekly`도 설치합니다. 도구가 필요 없으면 `--no-tools`로 건너뜁니다.

기본 보관함은 **설치를 실행한 Linux 사용자의 `~/Obsidian/Notes`**입니다.
Windows 사용자 이름과 Linux 사용자 이름이 달라도 됩니다.
설치 코드, 바로가기, 시작 노트의 경로는 실행 시 현재 사용자 홈으로 생성됩니다.

## 지원 범위

- Windows 11 또는 Windows 10 build 19044 이상, WSL2 + WSLg
- **x64 PC**, Ubuntu 22.04 이상 권장
- 이 구성의 실제 앱 동작 검증: Ubuntu 26.04 / WSLg 1.0.71
- ARM64, 일반 Linux 데스크톱, 원격/네트워크 보관함은 이번 배포의 검증 범위에 포함되지 않습니다.
- **Windows에 Antigravity 2.0이 설치되어 있어야 합니다.** 설치는 이 저장소의 범위가 아니며 사용자가 직접 합니다.
- Antigravity 로그인에 사용할 본인 계정이 필요합니다. 기업 계정은 조직의 제품 이용 권한이 필요합니다.

## 빠른 설치 (명령 한 줄)

WSL Ubuntu와 Windows용 Antigravity 2.0이 설치되어 있으면, **Ubuntu 터미널에서 아래 한 줄**로 나머지 자동 설치를 끝낼 수 있습니다.
Antigravity CLI(`agy`)나 Git 인증 준비는 필요 없습니다.

```bash
curl -fsSL https://raw.githubusercontent.com/AIMEDBIO-DEV/antigravity-obsidian-wsl/main/bootstrap.sh | bash
```

- 보관함 구성은 묻지 않고 **cmc**(CMC 팀 구조·규칙·템플릿)로 설치합니다. 빈 보관함은 `bash -s -- --profile minimal`로 지정합니다.
- sudo 암호를 **한 번** 묻습니다.
- 저장소를 `~/apps/antigravity-obsidian-wsl`에 내려받고(이미 있으면 갱신) `./setup.sh`를 실행합니다.
- 옵션은 그대로 `setup.sh`에 전달됩니다. 예: `curl -fsSL …/bootstrap.sh | bash -s -- --profile minimal --no-tools`
- 저장소에 로컬 변경이 있으면 갱신하지 않고 그대로 사용합니다. 기존 노트는 건드리지 않습니다.

자동 설치 후에도 **Antigravity 로그인·WSL 연결·보관함 열기**, (CMC) **플러그인 신뢰·Templater 자동 실행 허용**,
**Obsidian 한글 입력 확인**은 직접 진행합니다. 설치 마지막에 출력되는 안내와 아래 [5. 앱 실행과 최초 연결](#5-앱-실행과-최초-연결)을 따르세요.
설치부터 사용 확인까지 대화로 안내받으려면 아래 CLI 방식을 사용합니다.

## 설치 흐름과 역할

**선행 준비 → 저장소 내려받기 → Antigravity CLI에 한 번 설치 요청**으로 진행합니다.
CLI는 자동 설정 후에도 Antigravity의 WSL 연결·보관함 열기·Obsidian 한글 입력·노트 열람 확인까지 같은 대화에서 안내합니다.

| 구분 | 담당 범위 |
| --- | --- |
| 사용자 선행 작업 | WSL2/WSLg Ubuntu 설치, Windows용 Antigravity 2.0 설치, Ubuntu의 Antigravity CLI(`agy`) 설치·로그인, GitHub 저장소 접근 준비 |
| 이 저장소 | Obsidian, 필요한 라이브러리·글꼴·한글 입력기·바로가기·로컬 보관함, officecli, Node/pnpm, open-slide 작업공간(`~/Slides`)과 팀 테마 설치 |
| CLI가 끝까지 안내할 사용자 작업 | Antigravity 로그인·WSL 연결·보관함 열기, Obsidian 한글 입력·노트 열람 확인 |

**WSL과 Antigravity CLI 자체의 설치·계정 설정은 이 저장소의 자동화 범위 밖입니다.**
아래 선행 작업은 새 PC 사용자를 위한 안내입니다.
CLI(`agy`)는 Obsidian 설치 과정을 안내·진행하는 도구이며, 사용자가 Windows에 설치한 Antigravity 데스크톱 앱과 별개입니다.
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

## 2. 선행 작업: Windows Antigravity와 Ubuntu Antigravity CLI

Windows에는 Antigravity 2.0 데스크톱 앱을 평소 방식대로 설치하고 로그인해 둡니다.
이 저장소는 Windows 앱 설치를 다루지 않습니다.


다음으로 WSL Ubuntu 터미널에서 필요한 기본 도구와 CLI를 설치합니다.
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
이 저장소의 README.md와 AGENTS.md를 읽고 설치부터 실제 사용 확인까지 진행해 줘.
WSL2/WSLg, Antigravity CLI, Windows용 Antigravity 2.0은 이미 설치되어 있어.
./setup.sh --plan 확인 후 ./setup.sh를 실행해서 의존성·Obsidian·한글 입력기·보관함 설치,
터미널 숨김 Windows 바로가기 등록, 점검, Obsidian 실행까지 진행해 줘.
여기서 끝내지 말고 Windows Antigravity의 WSL 연결, 같은 보관함 열기,
Obsidian 한/영 키 입력, Antigravity에서 새 노트 작성 후 Obsidian에서 열람까지 이어서 확인해 줘.
로그인이나 화면 조작이 필요하면 내가 할 일을 한 단계씩 안내하고, 완료하면 계속해 줘.
CMC 팀 구조·규칙도 포함하려면 --profile cmc로 설치하고, 플러그인 신뢰와 PC별 Templater 자동 실행 허용까지 안내해 줘.
officecli와 open-slide(~/Slides, cmc-weekly 테마)도 설치되니, docx 한 장 생성과 슬라이드 미리보기 화면 확인까지 이어서 해 줘.
현재 Linux 사용자 경로를 사용하고 기존 노트·인증·MCP 설정은 보존해 줘.
검증하지 못한 항목을 완료로 보고하지 마.
```

`sudo` 암호는 터미널의 암호 입력란에 입력합니다. CLI 대화에 암호를 적을 필요는 없습니다.
`setup.sh`가 자동 설정을 수행하고, `AGENTS.md`가 CLI의 후속 안내와 완료 기준을 정합니다.
사용자가 별도 설치 명령을 다시 요청할 필요는 없습니다. 로그인 등 사용자 작업이 끝나면
같은 대화에서 “완료했어, 계속해 줘”라고 알려 주세요.
CLI에 GUI 제어 도구가 없으면 Antigravity 연결·화면 확인은 사용자가 안내에 따라 진행합니다.
자동 단계 성공과 실제 사용 확인 완료는 구분해 보고합니다.

### CLI 없이 직접 설치하는 방법

같은 저장소 폴더에서 다음 스크립트를 직접 실행해도 됩니다.

```bash
# 변경 없이 전체 단계 확인
./setup.sh --plan

# 의존성부터 숨김 바로가기·입력 검사·Obsidian 실행 요청까지
./setup.sh
```

ZIP으로 받았고 실행 권한이 없다면 먼저 실행합니다.

```bash
chmod +x setup.sh install.sh scripts/install-deps.sh
```

문서·슬라이드 도구는 기본으로 함께 설치됩니다. 건너뛰거나 작업공간 경로를 바꾸려면:

```bash
./setup.sh --no-tools                       # officecli, Node/pnpm, open-slide 생략
./setup.sh --slides "$HOME/Decks"           # 슬라이드 작업공간 경로 지정 (기본 ~/Slides)
```

다른 로컬 보관함 경로를 사용하려면:

```bash
./setup.sh --vault "$HOME/Obsidian/Research Notes"
```

`sudo ./setup.sh`나 `sudo ./install.sh`로 실행하지 마세요. 일반 Linux 사용자로 실행합니다.
`setup.sh`는 Obsidian을 실행하지만 Antigravity 로그인·연결을 대신하지는 않습니다.
앱 설치 이후 단계만 재개하려면 `./setup.sh --finish-only`를 실행합니다.
기존 의존성과 캐시만 쓰려면 `./setup.sh --offline`을 사용합니다(apt 실행 생략).
기존 `./install.sh`는 앱·입력기·보관함까지만 설치하는 하위 명령으로 유지합니다.

### 팀 구조·규칙을 포함한 설치

```bash
./setup.sh --plan --profile cmc
./setup.sh --profile cmc
```

CMC 프로필은 기본적으로 minimal과 같은 `~/Obsidian/Notes`에 규칙·템플릿·애드온을 적용하고 그 보관함을 등록합니다.
시작 문서는 `SETUP.md`, 새 참고 노트 폴더는 `References`입니다.
처음 설치할 때 프로필을 생략하면 cmc입니다. 일반 빈 보관함은 `--profile minimal`입니다. 재설치는 저장된 프로필/경로를 유지합니다.
`--finish-only`는 저장된 프로필의 시작 문서와 검증 항목을 이어갑니다.

CMC 첫 실행에서는 플러그인 사용 허용과 **Templater 자동 실행의 PC별 허용**이 필요합니다.
이후 8개 폴더·Daily의 실제 노트 생성과 규칙 검증을 마쳐야 전체 완료입니다.
자세한 절차는 [번들 안내](vault-templates/README.md)와 설치된 `SETUP.md`에 있습니다.

## 5. 앱 실행과 최초 연결

`./setup.sh`는 아래 바로가기 등록과 Obsidian 실행을 자동으로 진행합니다.
다음 내용은 CLI가 안내할 최초 연결 절차와 수동 복구 방법입니다.
`./install.sh`만 실행했거나 바로가기를 개별 갱신하려면 Ubuntu 저장소 폴더에서 실행합니다.

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$(wslpath -w "$PWD/scripts/create-windows-shortcuts.ps1")" -Distribution "$WSL_DISTRO_NAME"
```

이 명령은 **Obsidian (WSL)** 바로가기를 Windows 바탕화면 및
시작 메뉴의 **WSL Notes** 폴더에 만듭니다. Windows 사용자명, OneDrive 바탕화면 위치,
해당 WSL 배포판의 기본 Linux 사용자·홈 경로를 자동으로 확인합니다.
기존 같은 이름의 바로가기 대상이 다르면 백업을 만든 뒤 갱신합니다.
바로가기는 `wscript.exe` → VBScript → `wsl.exe` 순서로 실행하며, 콘솔 창을 숨깁니다.
등록 전에 동일한 방식의 임시 바로가기로 Linux 명령의 실제 실행을 검사합니다.
런처 파일은 Windows의 `%LOCALAPPDATA%\WSL Notes\Launchers`에 저장됩니다.
기존 바로가기도 위 등록 명령을 다시 실행하면 창 숨김 방식으로 갱신됩니다.
이 바로가기 도구에서는 배포판·Linux 사용자 이름에 공백이 없어야 합니다(예: `Ubuntu`, `Ubuntu-24.04`).
`WSL_E_DISTRO_NOT_FOUND`가 표시되는 이전 바로가기는 위 등록 명령을 다시 실행해 갱신하세요.
일부 WSL 버전은 바로가기의 배포판·사용자 이름에 붙인 따옴표를 이름의 일부로 처리하므로,
등록 도구는 해당 인수에 불필요한 따옴표를 넣지 않습니다.

바로가기를 더블클릭하면 Obsidian이 WSLg로 실행됩니다. WSLg를 별도로 시작할 필요는 없습니다.
다중 모니터에서 최대화 후 커서 좌표가 어긋나면, 최대화를 해제하고 **F11 전체화면**을 사용해 보세요.
검증한 PC에서는 F11 전환이 정상 동작했습니다.

Ubuntu 터미널에서 직접 실행할 수도 있습니다.

```bash
~/.local/bin/obsidian-wsl
```

1. Obsidian에서 설치 메시지의 보관함을 확인합니다. minimal은 `시작하기.md`, CMC는 `SETUP.md`를 엽니다.
   설치 중 Obsidian이 실행 중이었다면 **Open folder as vault**로 설치 완료 메시지의 경로를 직접 선택합니다.
2. Windows의 Antigravity 2.0에서 본인의 개인/기업 계정으로 로그인합니다.
3. Antigravity의 **Windows Subsystem for Linux** 기능(*Run the app against a Linux environment*)으로
   이 배포판에 연결합니다. 연결하면 앱이 선택한 WSL 배포판으로 다시 시작됩니다.
4. 연결된 Antigravity에서 설치 결과의 **절대 경로**(Linux 경로)를 프로젝트 폴더로 엽니다.
   Ubuntu에서 `realpath ~/Obsidian/Notes`로 확인할 수 있습니다.
   `~`나 `$HOME`을 GUI에 그대로 붙여넣지 마세요.

minimal 프로필 예시 요청(CMC는 설치된 AGENTS.md를 읽고 References에 type: reference 노트를 작성):

```text
이 프로젝트는 로컬 Obsidian 보관함이야.
Inbox/첫 메모.md를 한국어 Markdown으로 작성해 줘.
내용은 이번 주 업무 정리 방법이고, [[시작하기]] 링크를 포함해 줘.
실제 파일로 저장해 줘. 기존 노트와 .obsidian 설정은 변경하지 마.
```

Obsidian에서 `Inbox/첫 메모.md`가 나타나는지 확인합니다.
같은 폴더를 사용하는 방식이므로 노트 작성에 별도 MCP나 동기화 플러그인은 필요하지 않습니다.
동일 노트를 두 앱에서 동시에 수정하면 편집 충돌이 생길 수 있습니다.

## 문서·슬라이드 도구

`setup.sh`(또는 `python3 scripts/tools.py`)가 다음을 순서대로 준비합니다. 모두 일반 사용자 권한으로 동작하며 `sudo`가 필요 없습니다.

| 도구 | 설치 방식 |
| --- | --- |
| **officecli** | 공식 설치 스크립트 실행. `~/.local/bin/officecli`. 이미 설치되어 있으면 건너뜁니다. |
| **Node** | `^20.19 \|\| >=22.12` 조건을 만족하는 Node가 PATH에 있으면 그대로 사용합니다. 없으면 [tools.json](tools.json)의 **고정 버전·SHA-256**으로 `~/.local/share/wsl-notes/node/`에 설치합니다. |
| **pnpm** | 이미 있으면 유지합니다. 없으면 고정 버전을 `~/.local/share/wsl-notes/tools/`에 설치합니다(전역 설정 변경 없음). |
| **open-slide** | `@open-slide/cli@latest`로 `~/Slides`에 작업공간을 만들고 의존성을 설치합니다(**버전 미고정**). 폴더가 이미 있으면 그대로 두고, open-slide가 아닌 폴더면 중단합니다. |
| **cmc-weekly 테마** | [slide-templates/](slide-templates/README.md)의 테마·로고·Pretendard 웹폰트·PPTX 표 변환 스크립트를 `~/Slides/themes`, `~/Slides/assets`, `~/Slides/scripts`에 **없는 파일만** 복사합니다. |

**신뢰 범위:** Obsidian·Node는 해시로 검증하지만 **officecli와 open-slide는 버전을 고정하지 않습니다.**
officecli는 공식 스크립트를 그대로 신뢰하고 자동 업데이트도 하며, open-slide는 설치 시점의 최신판(`latest`)을 받습니다.
따라서 PC마다 버전이 다를 수 있고, 설치된 open-slide 버전은 `tools-install.json`의 `open_slide_core`에 기록됩니다.
기존 작업공간의 open-slide는 `pnpm up @open-slide/core`로 직접 올립니다.
공식 스크립트는 `~/.local/bin`이 PATH에 없으면 `~/.bashrc`에 PATH 한 줄을 추가합니다.
스크립트가 감지된 에이전트 폴더에 skill을 넣지만 Antigravity 폴더는 감지하지 못할 수 있으므로,
설치기가 Antigravity 전역 경로 `~/.gemini/config/skills/officecli/SKILL.md`와 `~/.agents/skills/officecli/SKILL.md` 중 없는 쪽을 채웁니다. 한쪽에 있으면 그 파일을 복사하고, 둘 다 없으면 내려받습니다(기존 파일은 유지).

### 사용

**슬라이드 미리보기는 터미널 대신 대화로 엽니다.** WSL에 연결된 Antigravity 데스크톱 앱에서 이렇게 요청하세요.

> 슬라이드 미리보기 열어줘

설치기가 넣어 둔 전역 skill(`slides-preview`)에 따라 에이전트가 `slides-wsl start`로 서버를 백그라운드에서 띄웁니다.
서버가 준비되면 Windows 브라우저가 열리고, 에이전트가 주소(기본 `http://localhost:5173`)를 알려 줍니다.
“미리보기 꺼줘”라고 하면 서버를 종료합니다. 슬라이드를 고치면 열린 화면에 바로 반영되므로 다시 켤 필요가 없습니다.

슬라이드 작성도 같은 방식입니다. 예: “`/create-slide`로 이번 주 주간 보고를 cmc-weekly 테마로 만들어 줘.”
개발 서버의 **Themes** 패널에서 `cmc-weekly` 데모를 확인할 수 있습니다.
PPTX로 내보낼 때 표를 PowerPoint에서 편집할 수 있는 표로 바꾸는 방법은 [slide-templates/README.md](slide-templates/README.md#pptx로-내보낼-때-표를-네이티브-표로-바꾸기)를 참고하세요.
브라우저가 자동으로 열리지 않으면 에이전트가 알려 준 주소를 Windows 브라우저에 직접 입력하세요.

터미널을 쓰는 경우 같은 명령을 직접 실행할 수 있습니다.

```bash
officecli --version
~/.local/bin/slides-wsl start    # 백그라운드 실행 후 브라우저 열기 (이미 실행 중이면 브라우저만)
~/.local/bin/slides-wsl status   # 실행 중이면 주소 출력
~/.local/bin/slides-wsl stop     # 종료
~/.local/bin/slides-wsl          # 앞쪽에서 실행, Ctrl+C로 종료
```

### 문제 해결

- **`officecli`를 찾을 수 없음:** 새 터미널을 열거나 `source ~/.bashrc`를 실행합니다. 그래도 없으면 `~/.local/bin/officecli`를 확인합니다.
- **`~/Slides`가 open-slide 폴더가 아니라며 중단:** 기존 폴더는 수정하지 않습니다. `--slides`로 다른 경로를 지정하세요.
- **도구 설치 실패:** 원인을 해결하고 `python3 scripts/tools.py`만 다시 실행하면 됩니다. 이미 만든 결과는 유지됩니다.
- **`--offline`:** 네트워크가 필요한 단계는 건너뛰고 그 사실을 표시합니다. 완료로 기록되지 않으므로 연결 후 다시 실행하세요.
- 스캐폴더는 일부 특수문자가 든 경로를 거부합니다. 작업공간 경로에는 공백·따옴표를 피하세요.

## 설치되는 항목

| 항목 | 위치 |
| --- | --- |
| Obsidian 버전별 파일 | `~/.local/share/wsl-notes/apps/obsidian/` |
| 실행 명령 | `~/.local/bin/obsidian-wsl` |
| 앱 전용 URL 도우미 | `~/.local/share/wsl-notes/bin/xdg-open` |
| Linux 시작 메뉴 항목 | `~/.local/share/applications/obsidian-wsl.desktop` |
| 다운로드 캐시 | `~/.cache/wsl-notes/` |
| 설치 기록 | `~/.local/share/wsl-notes/install.json` |
| 기본 보관함 | `~/Obsidian/Notes` |
| 슬라이드 작업공간 | `~/Slides` (테마: `themes/cmc-weekly.*`, 로고: `assets/cmc-weekly/image1~3.png`, 글꼴: `assets/fonts/pretendard/`, 도구: `scripts/`) |
| 슬라이드 실행 명령 | `~/.local/bin/slides-wsl` (`start`/`status`/`stop`), 로그 `~/.local/state/wsl-notes/slides-dev.log` |
| 미리보기 에이전트 지침 | `~/.gemini/config/skills/slides-preview/SKILL.md` (Antigravity 전역 skill) |
| officecli | `~/.local/bin/officecli`, skill: `~/.gemini/config/skills/officecli/`(Antigravity), `~/.agents/skills/officecli/` |
| Node(없을 때만) / pnpm(없을 때만) | `~/.local/share/wsl-notes/node/`, `~/.local/share/wsl-notes/tools/` |
| 도구 설치 기록 | `~/.local/share/wsl-notes/tools-install.json` |

Obsidian 바이너리는 저장소에 포함하지 않고 공식 배포처에서 내려받습니다. Antigravity는 설치하지 않습니다.
[versions.json](versions.json)의 버전과 SHA-256을 확인한 뒤 설치합니다.
해시는 검증에 사용한 배포 파일의 해시이며, 공급업체 서명을 대신하지 않습니다.
현재 고정 버전은 Obsidian **1.13.7**입니다.

설치기는 기존 노트와 보관함 설정을 덮어쓰지 않습니다.
Obsidian의 보관함 목록에 새 경로를 추가할 때 기존 목록을 유지하고 원본 JSON을 백업합니다.
기존 사용자 인증이나 MCP 설정을 가져오는 작업은 하지 않습니다.
앱 자체가 최초 실행 시 이전 제품 설정을 마이그레이션할 수는 있습니다.

URL 도우미는 이 설치의 Obsidian에만 적용하며 시스템 `xdg-open`을 바꾸지 않습니다.
HTTP/HTTPS 링크는 Windows 기본 브라우저로 엽니다.

## 보관함 규칙 템플릿 (선택)

설치기가 만드는 보관함은 폴더 3개와 시작 노트만 있는 빈 상태입니다.
팀에서 쓰는 노트 작성 규칙(폴더별 노트 종류, frontmatter 필수 항목, 태그 목록, 검증 스크립트)을
얹으려면 `vault-templates/`의 템플릿을 적용합니다.

```bash
python3 scripts/vault.py --plan          # 대상 경로와 단계 확인
python3 scripts/vault.py --validate      # ~/Obsidian/Notes에 적용하고 규칙 검증
```

선택한 CMC 프로필은 `setup.sh --profile cmc`의 설치 흐름에 포함됩니다.
없는 파일만 쓰고 기존 노트는 덮어쓰지 않습니다.
자세한 내용은 [vault-templates/README.md](vault-templates/README.md)를 참고하세요.

## 점검 및 문제 해결

```bash
python3 scripts/doctor.py
```

- **기존 실행 파일 충돌:** 설치기가 만들지 않은 동일 이름의 launcher는 덮어쓰지 않습니다.
  표시된 기존 파일을 확인하고 별도 이름으로 백업한 뒤 재시도하세요.
- **라이브러리 누락:** `./scripts/install-deps.sh`를 실행한 뒤 다시 설치합니다.
- **한글이 네모로 표시:** 의존성 설치 후 Obsidian을 종료하고 다시 실행합니다.
  한글 표시용 글꼴과 입력기는 별개입니다. 입력이 안 되면 아래 한글 입력 항목을 확인하세요.
- **창이 작업표시줄에만 뜨고 화면에 안 보임:** 일부 PC에서는 WSL의 systemd가 WSLg 화면 출력을 막습니다.
  `/etc/wsl.conf`의 `[boot]`에 `systemd=false`를 두고 Windows에서 `wsl --shutdown` 후 다시 엽니다.
  한글 입력기는 systemd 없이도 동작합니다.
- **검은 화면/Wayland 문제:** 일회성으로 `~/.local/bin/obsidian-wsl --ozone-platform=x11`을 시도합니다.
- **sandbox 오류:** root로 실행하지 마세요. `--no-sandbox`를 기본 실행 옵션으로 추가하지 않습니다.
  배포판의 AppArmor/user namespace 정책은 관리자와 확인하세요.
- **MCP Error:** 노트 파일 작성에 MCP는 필요하지 않습니다. 기존 MCP 오류는 별도로 진단합니다.
- **Antigravity 연결·폴더 선택:** GUI에서 사용자가 직접 진행합니다. 화면 좌표를 이용한 자동 입력은 하지 않습니다.

Antigravity는 이 저장소 밖(Windows 앱)이므로 문제 해결은 해당 앱의 안내를 따릅니다.
로그에 인증 관련 값이 포함될 수 있으므로 원문을 저장소에 올리지 마세요.

## 재설치·업데이트·제거

같은 버전으로 다시 실행해도 기존 노트는 유지됩니다.
캐시를 미리 받은 환경에서는 `./install.sh --offline`을 사용할 수 있습니다.
버전 업데이트는 유지보수자가 공식 URL/해시를 갱신하고 검증한 저장소 버전을 받아 다시 설치합니다.
앱 자체의 자동 업데이트 동작은 제품에 따라 다르므로 설치 기록과 실제 앱 버전은 달라질 수 있습니다.

제거하려면 Obsidian을 종료하고 위 표의 앱 파일, 실행 명령, 시작 메뉴 항목을 삭제합니다.
**`~/Obsidian/Notes`, `~/Slides` 및 앱 사용자 설정은 별도 데이터이므로 보존하세요.**
도구는 `~/.local/bin/slides-wsl stop`으로 서버를 끈 뒤 `~/.local/bin/slides-wsl`, `~/.local/bin/officecli`, `~/.gemini/config/skills/slides-preview/`와 `~/.local/share/wsl-notes/{node,tools}`를 삭제하면 제거됩니다.
이 도구는 노트 삭제 명령을 제공하지 않습니다.

## 한글 입력

의존성 설치 시 `ibus`, `ibus-hangul`, GTK 입력 모듈을 설치하고, 앱 설치 시
두벌식 입력과 `한/영` 키·오른쪽 Alt·`Shift+Space` 전환을 설정합니다.
이 입력기는 WSLg로 실행하는 **Obsidian**용입니다. Windows의 Antigravity는 Windows 입력기를 사용합니다.
Obsidian 실행 명령은 사용자 서비스 `wsl-notes-ibus.service`를 자동으로 시작하고
X11 및 IBus 환경에서 앱을 실행합니다. WSL 재시작 후에도 바로가기 실행으로 적용됩니다.
`/etc/wsl.conf`에서 systemd를 끈 환경(`[boot] systemd=false`)에서는 사용자 서비스 대신
세션 D-Bus와 `ibus-daemon`을 직접 시작합니다. 모드는 실행 시 자동으로 판단합니다.

1. 설정 변경 후 실행 중인 Obsidian을 완전히 종료하고 바로가기로 다시 엽니다.
2. Windows 입력 상태를 영문으로 둡니다.
3. Obsidian 입력창에서 **한/영 키** 또는 **Shift+Space**로 전환합니다.
   한/영 키가 오른쪽 Alt로 전달되는 키보드도 지원합니다.

한글 입력기는 처음에는 영문 모드입니다. Windows가 한/영 키를 먼저 처리하는
환경에서는 `Shift+Space`를 사용하세요. Ubuntu 26.04 / WSLg 1.0.71에서
사용자가 실제 Obsidian의 `Shift+Space`와 한/영 키 입력을 확인했습니다.

기존 저장소 설치는 `git pull` 후 `scripts/install-deps.sh`, `./install.sh`를 다시
실행하면 갱신됩니다. 앱 파일이 검증된 캐시에 있으면 `./install.sh --offline`도 가능합니다.
설치 프로그램은 사용자 IBus 공용 설정을 변경하며, 기존 설정을
`~/.local/share/wsl-notes/backups/before-korean-input/{general,hangul}.dconf`에 최초 한 번 백업합니다.
입력기 서비스는 앱 실행 시 시작하므로 별도의 부팅 자동 시작 등록은 필요하지 않습니다.

입력 엔진 설명: [IBus Hangul](https://github.com/libhangul/ibus-hangul).

자동 단계 상태는 `~/.local/share/wsl-notes/setup-status.json`에 기록됩니다.
앱 실행 요청만으로 화면이나 로그인 성공을 판정하지 않으며, CLI는 실제 확인 후
`user_checks_pending`을 갱신합니다. 완료 기준은 [AGENTS.md](AGENTS.md)를 참고하세요.

## 개발 및 검증

```bash
python3 -m unittest discover -s tests -v
bash -n bootstrap.sh setup.sh install.sh scripts/install-deps.sh scripts/wsl-notes-ime.sh
# WSLg에서 설치 후 실제 입력 엔진 조합 검증 (Obsidian 입력창과 별도 컨텍스트)
/usr/bin/python3 scripts/verify-korean-input.py
/usr/bin/python3 scripts/verify-korean-input.py Alt_R
/usr/bin/python3 scripts/verify-korean-input.py Hangul
```

테스트는 임시 사용자 홈에서 경로의 공백·특수문자, 재실행, 기존 노트/설정 보존,
다운로드 해시 검사와 압축 경로 검사를 확인합니다. 실제 Antigravity WSL 연결·노트 생성·Obsidian 열람은 해당 PC에서 별도로 확인합니다.

## 참고

- [Antigravity 공식 다운로드](https://antigravity.google/download)
- [Obsidian 공식 다운로드](https://obsidian.md/download)
- [open-slide](https://github.com/1weiho/open-slide) · [OfficeCLI](https://github.com/iOfficeAI/OfficeCLI)
- [Microsoft WSL GUI 앱 안내](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)

Antigravity, Obsidian, officecli, open-slide, Node는 각 공급업체·프로젝트가 배포하는 별도 제품이며 해당 이용 조건이 적용됩니다.
이 저장소는 이들 제품의 공식 설치 도구가 아닙니다.
