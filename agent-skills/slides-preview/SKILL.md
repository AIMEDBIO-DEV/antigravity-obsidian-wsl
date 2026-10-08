---
name: slides-preview
description: >-
  open-slide 슬라이드 미리보기(개발 서버)를 사용자 대신 켜고 끈다. 사용자가 "슬라이드 미리보기 열어줘",
  "슬라이드 보여줘", "미리보기 서버 켜줘/꺼줘", "open the slide preview"처럼 요청하거나,
  슬라이드를 만들거나 고친 뒤 결과를 보여 줘야 할 때 사용한다.
---
<!-- # Managed by antigravity-obsidian-wsl — 재설치 시 덮어써집니다. 직접 고치려면 이 줄을 지우세요. -->

# 슬라이드 미리보기

사용자는 터미널을 쓰지 않는다. 서버 실행·종료·문제 확인은 에이전트가 맡고, 사용자에게 명령어를 입력하라고 하지 않는다.
명령은 WSL 터미널에서 실행한다. Antigravity가 WSL에 연결되어 있지 않으면 먼저 연결해 달라고 안내한다.

## 열기

```bash
~/.local/bin/slides-wsl start
```

- 서버를 백그라운드로 띄우고, 응답할 때까지 기다린 뒤 Windows 브라우저를 연다. 이미 실행 중이면 브라우저만 다시 연다.
- 명령은 몇 초 안에 끝난다. 끝나지 않는 `slides-wsl`(인자 없음)이나 `pnpm dev`를 직접 실행하지 않는다. 대화가 그 명령에 묶인다.
- 출력의 URL(`http://localhost:5173` 등)을 사용자에게 알려 준다. 브라우저가 안 열렸다고 하면 그 주소를 Windows 브라우저에 붙여 넣게 한다.
- 특정 덱을 보여 줄 때는 `<URL>s/<slide-id>` 주소를 함께 알려 준다(`<slide-id>`는 `~/Slides/slides/` 아래 폴더 이름).

## 상태 확인과 종료

```bash
~/.local/bin/slides-wsl status   # 실행 중이면 URL 출력, 중지 상태면 종료 코드 3
~/.local/bin/slides-wsl stop     # 사용자가 끄라고 할 때만
```

슬라이드 파일을 고치면 열린 미리보기에 바로 반영되므로 서버를 다시 시작할 필요가 없다.

## 실패했을 때

`start`가 실패하면 출력된 로그 마지막 부분을 읽고 원인을 설명한다. 전체 로그는 `~/.local/state/wsl-notes/slides-dev.log`에 있다.

- `slides-wsl`이 없음: 도구 설치가 안 된 상태다. 저장소의 `python3 scripts/tools.py`로 설치한다.
- 의존성 오류(`Cannot find module` 등): `~/Slides`에서 `pnpm install` 후 다시 `start`.
- 포트 충돌: 다른 프로그램이 5173을 쓰면 open-slide가 다음 포트를 쓴다. 출력된 URL을 그대로 안내한다.
