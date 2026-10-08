# 슬라이드 테마 번들

`setup.sh`가 `~/Slides`(open-slide 작업공간)에 설치하는 팀 공통 테마입니다.
`vault-templates/`와 같은 원칙으로 **없는 파일만 복사**하고, 이미 있는 파일은 덮어쓰지 않습니다.
팀이 수정한 테마를 재설치가 되돌리지 않습니다.

| 번들 | 내용 |
| --- | --- |
| `cmc-weekly/` | CMC 주간 보고 테마: 표지, 목차·요약 표, 공통 헤더, 본문 슬라이드, 개조식 제목 지침, Pretendard 웹폰트, PPTX 네이티브 표 변환 |

## 구성

```text
slide-templates/<id>/
├── themes/<id>.md         디자인 규칙(팔레트, 글꼴, 제목 작성법, 붙여넣기용 컴포넌트, 표·PPTX 규칙)
├── themes/<id>.demo.tsx   개발 서버의 Themes 패널이 미리보기로 쓰는 데모
├── assets/<id>/           데모와 덱이 import하는 로고·배너 이미지 (@assets/<id>/...)
├── assets/fonts/          덱이 @font-face로 등록하는 웹폰트 (선택)
└── scripts/               내보내기 후처리 등 작업공간 도구 (선택)
```

설치기는 이 구조 그대로 `~/Slides/{themes,assets,scripts}`에 복사합니다.
`themes/<id>.md`는 open-slide의 `/create-slide` skill이 새 슬라이드를 만들기 전에 읽습니다.
데모·문서가 `assets/`와 `scripts/`의 파일을 경로로 참조하므로 모두 함께 배포합니다
(`tests/test_tools.py`가 참조 경로가 실제로 있는지 검사합니다).

## cmc-weekly 테마의 주요 규칙

- **개조식 제목:** 본문 제목·결론 문구는 명사형으로 끝나는 한 줄 라벨로 씁니다. 강조는 한 곳만 하고, 표·차트가 메시지인 페이지는 제목을 생략합니다. 자세한 규칙과 전/후 예시는 `themes/cmc-weekly.md`의 *Slide Title Writing*에 있습니다.
- **Pretendard 웹폰트:** 모든 덱은 `index.tsx` 맨 위에서 `assets/fonts/pretendard/`의 서브셋을 `@font-face`로 등록합니다.
  그래서 PC에 글꼴이 없어도 viewer·PDF·HTML 내보내기의 글꼴이 같습니다. 글꼴은 SIL OFL 1.1이며 `LICENSE.txt`를 함께 배포합니다.
- **표는 진짜 `<table>`로:** 원본 PPT에서 표인 것은 grid나 div로 흉내 내지 않고 `<table>` + `<colgroup>` + `rowSpan`/`colSpan`으로 작성합니다.

## PPTX로 내보낼 때 표를 네이티브 표로 바꾸기

open-slide(`@open-slide/core` 2.x)의 **Export → PPTX**에는 표 기능이 없습니다.
그래서 셀마다 사각형과 텍스트 상자가 따로 생깁니다. 아래 후처리를 거치면 PowerPoint에서 편집할 수 있는 표(`<a:tbl>`)로 바뀝니다.

1. 개발 서버(`slides-wsl`)에서 덱을 열고 **Export → PPTX**로 내보냅니다.
2. 같은 덱을 `/s/<slide-id>`로 연 상태에서 `~/Slides/scripts/extract-tables.js` 내용을 브라우저 콘솔에 붙여 넣습니다.
   1페이지부터 마지막 페이지까지 넘기며 표의 위치·병합·채우기·테두리·글자를 기록하고 `tables.json`을 내려받습니다.
3. 변환합니다(Python 표준 라이브러리만 사용):

   ```bash
   cd ~/Slides
   python3 scripts/pptx-native-tables.py "<내보낸 파일>.pptx" tables.json "<이름> (표 적용).pptx"
   ```

   표 영역 안의 셀 도형을 지우고, 같은 크기·병합·서식의 표를 그 자리에 넣습니다. 표 밖의 도형은 그대로 둡니다.
   PPTX 표의 글꼴은 맑은 고딕입니다. PowerPoint에는 웹폰트가 포함되지 않으므로 어느 PC에서나 같은 모양으로 보이게 하기 위해서입니다.

## 규칙

- **데모에는 가상의 예시 데이터만 넣습니다.** 이 저장소는 공개이므로 실명, 협력사명,
  과제·물질 코드, 실제 진행 상황을 넣지 않습니다. `tests/test_tools.py`가 알려진 항목의 재유입을 검사합니다.
- 회사 로고·배너는 포함되어 있습니다. 교체하려면 같은 파일명으로 `assets/`를 바꾸세요.
- 새 테마는 `slide-templates/<id>/`를 만들고 `tools.json`의 `themes`에 `<id>`를 추가합니다.
- 실제 업무 슬라이드(`slides/<id>/`)와 원본 pptx는 이 저장소에 넣지 않습니다.

## 수동 적용

```bash
cp -rn slide-templates/cmc-weekly/{themes,assets,scripts} ~/Slides/
```
