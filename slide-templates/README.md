# 슬라이드 테마 번들

`setup.sh`가 `~/Slides`(open-slide 작업공간)에 설치하는 팀 공통 테마입니다.
`vault-templates/`와 같은 원칙으로 **없는 파일만 복사**하고, 이미 있는 파일은 덮어쓰지 않습니다.
팀이 수정한 테마를 재설치가 되돌리지 않습니다.

| 번들 | 내용 |
| --- | --- |
| `cmc-weekly/` | CMC 주간 보고 테마: 표지, 목차·요약 표, 공통 헤더, 본문 슬라이드 |

## 구성

```text
slide-templates/<id>/
├── themes/<id>.md         디자인 규칙(팔레트, 글꼴, 붙여넣기용 컴포넌트)
├── themes/<id>.demo.tsx   개발 서버의 Themes 패널이 미리보기로 쓰는 데모
└── assets/                데모가 import하는 로고·배너 이미지
```

`themes/<id>.md`는 open-slide의 `/create-slide` skill이 새 슬라이드를 만들기 전에 읽습니다.
데모가 `../assets/image*.png`를 import하므로 세 부분은 항상 함께 배포합니다.

## 규칙

- **데모에는 가상의 예시 데이터만 넣습니다.** 이 저장소는 공개이므로 실명, 협력사명,
  과제·물질 코드, 실제 진행 상황을 넣지 않습니다. `tests/test_tools.py`가 알려진 항목의 재유입을 검사합니다.
- 회사 로고·배너는 포함되어 있습니다. 교체하려면 같은 파일명으로 `assets/`를 바꾸세요.
- 새 테마는 `slide-templates/<id>/`를 만들고 `tools.json`의 `themes`에 `<id>`를 추가합니다.
- 실제 업무 슬라이드(`slides/<id>/`)와 원본 pptx는 이 저장소에 넣지 않습니다.

## 수동 적용

```bash
cp -n slide-templates/cmc-weekly/themes/* ~/Slides/themes/
cp -n slide-templates/cmc-weekly/assets/*  ~/Slides/assets/
```
