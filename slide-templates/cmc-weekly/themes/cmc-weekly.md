---
name: CMC Weekly Report
description: Corporate CMC weekly progress deck matching the Red & Gray laboratory report standard — authentic Slide 1 cover with hero banner & red card, master header with document title, 3-color status legend and company logo, Slide 2 project agenda table, Slide 6 universal header tracker, and Slide 20 regulatory Gantt chart.
mode: light
---

# CMC Weekly Report Theme

A precision engineering & CMC operational report theme extracted directly from the corporate CMC weekly deck (`Weekly Progress_CMC_YYMMDD.pptx`).

It defines the canonical slide layouts and master elements:
1. **Master Header (상단 공통 헤더)**:
   - **좌측 상단**: `[CMC] Weekly Progress 260101–260105` (또는 해당 기간/일자)
   - **중앙 상단**: 3색 진행상태 범례 (`● 계획대로 진행중` #68A490 / `● Minor 사항 있음` #EAC282 / `● 큰 issue 있음` #D65532)
   - **우측 상단**: 회사 공식 로고 (`image2.png` / `image3.png`) 및 `Written by | 담당자` 표 (1pt 검정 테두리, 라벨 셀 `#F2F2F2`, 20px 일반 굵기 — 아래 `WrittenBy`)
2. **Slide 1: Cover Archetype** — Crisp white canvas, middle hero graphic banner (`top: 175px`, `height: 728px`) with translucent white tint (84%), fixed left title group (`CMC REGULAR PROGRESS REPORT` category + `Weekly Progress <dates>` only, with no subtitle or extra widgets), and a vertical translucent Crimson Red rectangle (`#C00000`, 88% opacity) on the right containing centered "CMC Team" and the company logo in the bottom right corner.
3. **Slide 2: Table of Contents / Executive Summary Archetype** — Grouped by project tags (`[P001]`, `[P002]`, `[P003]`, `[P-EX]`), with structured 4-column tables: `EXP-No. | EXP title | 신규 추가된 내용 | 담당자`. Header row filled with Crimson Red (`#C00000`) and white text.
4. **Slide 6: Universal Content Slide Archetype** — Fixed `MasterHeader` + `TopHeaderTable` across the top of all content slides (1pt/2px **black** grid, light-gray `#F2F2F2` header rows, `#A6A6A6` M–F day cells, status column, researcher), followed by the content area.
5. **Slide 20: Regulatory Gantt Archetype** — Multi-swimlane regulatory and site initiation schedule with country badges, monthly timescale, and a vertical Crimson Red `Today` marker line.

## Palette

```
bg:           #ffffff   (Crisp laboratory white)
bgMuted:      #f4f5f7   (Muted table row / card background)
text:         #111827   (Deep charcoal black)
textMuted:    #4b5563   (Secondary body text / neutral metadata)
accent:       #c00000   (Primary Crimson Red - cover card, agenda headers, key alerts, Today marker)
headerBg:     #f2f2f2   (Standard top table header fill - neutral light gray)
headerBorder: #6b7280   (Crisp table border gray)
tableLine:    #000000   (Written by box + weekly tracker grid — 1pt black = 2px on the canvas)
dayFill:      #a6a6a6   (Tracker M–F body cells — bg1 lumMod 65%)
border:       #d1d5db   (Subtle card and cell divider gray)

/* 3-State Status Legend Colors (from PPT slideLayout13 TextBox 7) */
statusOnTrack: #68a490  (● 계획대로 진행중 - Soft Teal Green)
statusMinor:   #eac282  (● Minor 사항 있음 - Warm Amber)
statusIssue:   #d65532  (● 큰 issue 있음 - Coral Red)
```

## Typography

- **Display & Headings**: `Pretendard, "Malgun Gothic", "맑은 고딕", -apple-system, sans-serif`
- **Body & Tables**: `Pretendard, "Malgun Gothic", "맑은 고딕", -apple-system, sans-serif`
- **Scale**:
  - Hero (Slide Title): 54–64px / 800 bold
  - Master Header Title: 18–20px / 800 bold
  - Status Legend: 11–12px / 600 weight
  - Team Name on Cover: 54px / 800 bold (white)
  - Section Tag / Heading: 20–24px / 800 bold (`#c00000` or `#111827`)
  - Table Header: 12–13px / 700 bold
  - Table Body: 11–13px / 400–600 weight
  - Footnote / Metadata: 12–13px / 600 weight
  - Slide Title (본문 슬라이드 제목): 44px / 800 bold, line-height 1.25, 1~2줄 (개조식 — 아래 *Slide Title Writing* 참조)

### Webfont 로딩 (필수)

`fontFamily`에 `Pretendard`를 적는 것만으로는 Pretendard가 설치되지 않은 PC에서 맑은 고딕으로 대체된다. **모든 덱은 `index.tsx` 최상단(import 바로 아래, 페이지 컴포넌트 밖)에 아래 블록을 그대로 넣어** 저장소의 Pretendard 서브셋을 `@font-face`로 등록한다.

- 글꼴 파일: `assets/fonts/pretendard/` (SIL OFL 1.1, `LICENSE.txt` 포함) — `@assets/fonts/pretendard/...`로 import
- 모듈 레벨에서 한 번만 등록한다 (페이지마다 `<style>`을 렌더하지 않는다). `FONT_STYLE_ID`는 덱마다 고유하게 바꾼다.
- 이렇게 등록하면 viewer, PDF, **Export as HTML**(zip: `<id>.html` + `assets/`에 woff2 포함), PPTX 렌더가 모두 같은 글꼴을 쓴다.
- 필요한 굵기만 import한다. 기본은 400 / 700 / 800이고, 그 밖에 Medium(500), SemiBold(600), Black(900) 서브셋이 있다.
- 서브셋 범위: KS X 1001 한글 2,350자 전부 + 추가 430자, 라틴, 주요 기호(→ · — ≈)를 포함한다. 한자와 일부 희귀 한글은 없으므로, 해당 글자는 글자 단위로 `"Malgun Gothic"`으로 대체된다. 따라서 fallback 체인을 지우지 않는다.

```tsx
import pretendard400 from '@assets/fonts/pretendard/Pretendard-Regular.subset.woff2';
import pretendard700 from '@assets/fonts/pretendard/Pretendard-Bold.subset.woff2';
import pretendard800 from '@assets/fonts/pretendard/Pretendard-ExtraBold.subset.woff2';

// Pretendard webfont — registered once at module level (not per page) so every
// viewer / PDF / HTML export renders the same face regardless of locally installed fonts.
const FONT_STYLE_ID = 'osd-webfont-<slide-id>';
const fontCss = ([
  [400, pretendard400],
  [700, pretendard700],
  [800, pretendard800],
] as const)
  .map(
    ([weight, url]) =>
      `@font-face { font-family: 'Pretendard'; font-style: normal; font-weight: ${weight}; font-display: swap; src: url(${url}) format('woff2'); }`,
  )
  .join('\n');
if (typeof document !== 'undefined') {
  let fontStyle = document.getElementById(FONT_STYLE_ID);
  if (!fontStyle) {
    fontStyle = document.createElement('style');
    fontStyle.id = FONT_STYLE_ID;
    document.head.appendChild(fontStyle);
  }
  if (fontStyle.textContent !== fontCss) fontStyle.textContent = fontCss;
}
```

## Slide Title Writing (개조식)

본문 슬라이드의 제목·결론 문구는 **서술식이 아닌 개조식**(명사형·체언 종결)으로 작성한다. 결론과 핵심 키워드가 한눈에 읽히도록 *짧은 라벨형 문구*로 쓴다. (아래 전/후 표는 가상의 예시)

### 규칙

1. **명사·명사형으로 종결**한다. `~합니다 / ~입니다 / ~했습니다 / ~보입니다 / ~그칩니다` 같은 서술어미 금지. (예: …완료, …지연, …승인, …감소, …재시험, …대응 방안)
2. **짧게 — 한 줄(약 20~35자)**을 기본으로 한다. 한 제목에 주장 1개. 두 번째 주장·부연 수치는 본문 카드·표·각주로 옮긴다. 본문에 이미 보이는 수치를 제목에서 반복하지 않는다.
3. **주제 + 행동/결과**를 라벨처럼 쓴다. 조사(`은/는/이/가/을/를`)는 읽기 자연스러운 선에서 최소화하고, 연결은 `→`, `–`, `,`로 한다.
4. **강조는 1곳**. 핵심 키워드·수치 하나만 accent(`#c00000`)로 칠한다. 섹션·출처를 구분해야 하면 페이지 단위 테마색을 쓴다(예: 외부 자료 섹션 = 파랑 `#1f5fa8`, 자체 데이터 = 기본 빨강 `#c00000`). 같은 섹션 안에서는 한 가지 테마색만 쓰고, 헤더 선·섹션 라벨·막대·결론 박스가 함께 바뀌도록 `--osd-accent`를 페이지 루트에서 덮어쓴다.
5. **추측·완곡 어미 금지**. `~했던 것으로 보입니다` 같은 문장은 제목에서 빼고, 필요하면 각주·본문에 `추정` 표기로 둔다.
6. **기간·범위는 섹션 라벨·범례·각주에**, 날짜는 `2026년 3월 ~ 현재`처럼 **풀어서** 쓴다. (`26.3~9` 같은 약식 지양)
7. **결론 박스·카드 헤더·섹션 라벨도 개조식**. 결론이 여러 개면 한 문장으로 잇지 말고 `·` 불릿 2~3줄(각 줄 명사형 종결)로 분리한다.
8. **표·차트가 메시지인 페이지는 제목 생략**. 섹션 라벨만 두고 시각 자료를 크게 쓴다. (`SlideTitle`을 렌더하지 않음)
9. **미확정·예정 항목은 점선 + `(예정)` 표기**로 확정 데이터와 시각적으로 구분한다.

### 전/후 (가상 예시)

| 서술식 (지양) | 개조식 (권장) |
| --- | --- |
| 안정성 시험 3개월 시점 결과가 모두 기준에 적합한 것으로 확인되었습니다 | 안정성 3개월 시점 전 항목 적합 |
| 외관 시험에서 일부 OOS가 발생하여 재시험을 진행하고 있습니다 | 외관 OOS 발생 → 재시험 진행 |
| 시험기관 일정이 2주 늦어져 보고서 제출도 함께 지연될 것으로 보입니다 | 시험기관 일정 2주 지연 – 보고서 제출 영향 |
| 원료 재공급 일정이 확정되어 다음 배치 생산을 준비하고 있습니다 | 원료 재공급 확정, 다음 배치 생산 준비 |
| 제출 문서 11건 중 8건의 검토가 완료되었고 나머지는 이번 달 안에 끝납니다 | 제출 문서 검토 8/11건 완료 |
| 월별 생산 수율은 큰 변동 없이 안정적으로 유지되고 있습니다 | (제목 생략 — 차트 중심) |

결론 박스 예시 (개조식 불릿):

- ❌ 외관 OOS로 재시험을 진행 중이며, 결과에 따라 출하 일정이 바뀔 수 있어 시험기관과 일정을 다시 협의하고 있습니다
- ✅ · 외관 OOS 재시험 진행
  · 결과에 따른 출하 일정 변동 가능
  · 시험기관 일정 재협의

### Paste-ready: 제목 컴포넌트

```tsx
const Em = ({ children }: { children: React.ReactNode }) => (
  <span style={{ color: 'var(--osd-accent, #c00000)' }}>{children}</span>
);

// 사용: <SlideTitle>제출 문서 검토 <Em>8/11건</Em> 완료</SlideTitle>
// 제목 생략 페이지는 SlideTitle 자체를 렌더하지 않는다 (Shell의 title 선택 항목).
const SlideTitle = ({ children }: { children: React.ReactNode }) => (
  <h2
    style={{
      fontFamily: 'var(--osd-font-display, Pretendard, "Malgun Gothic", "맑은 고딕", sans-serif)',
      fontSize: 44,
      fontWeight: 800,
      lineHeight: 1.25,
      letterSpacing: '-0.02em',
      margin: '6px 0 0 0',
      color: '#111827',
    }}
  >
    {children}
  </h2>
);
```

## Paste-Ready Components

### 1. `MasterHeader` (SlideLayout13 / SlideLayout15 Top Header)

```tsx
import companyLogoRed from '@assets/cmc-weekly/image3.png';

export const MasterHeader = ({
  title = '[CMC] Weekly Progress 260101–260105',
  researcher = '담당자',
}: {
  title?: string;
  researcher?: string;
}) => (
  <div style={{ marginBottom: 10 }}>
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        height: 41,
      }}
    >
      {/* Left: Document Title / Date range */}
      <div style={{ fontSize: 18, fontWeight: 800, color: '#111827', letterSpacing: '-0.01em', whiteSpace: 'nowrap' }}>
        {title}
      </div>

      {/* Right Cluster: Status Legend + Written by + Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* 3-State Status Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, fontWeight: 600, whiteSpace: 'nowrap' }}>
          <span style={{ color: '#68a490' }}>● 계획대로 진행중</span>
          <span style={{ color: '#9ca3af' }}>/</span>
          <span style={{ color: '#eac282' }}>● Minor 사항 있음</span>
          <span style={{ color: '#9ca3af' }}>/</span>
          <span style={{ color: '#d65532' }}>● 큰 issue 있음</span>
        </div>

        {/* Written by box (spec: `WrittenBy` below) */}
        <WrittenBy researcher={researcher} />

        {/* Official Red Company Logo (visible on white background) */}
        <img src={companyLogoRed} alt="AimedBio Logo" style={{ height: 24, maxWidth: 140, objectFit: 'contain', display: 'block' }} />
      </div>
    </div>

    {/* Master Header Bottom Rule: Crimson red accent bar (70px) + Gray baseline across */}
    <div style={{ position: 'relative', width: '100%', height: 3, marginTop: 6 }}>
      <div style={{ position: 'absolute', left: 0, top: 0, width: 70, height: 3, background: '#c00000', zIndex: 2 }} />
      <div style={{ position: 'absolute', left: 0, right: 0, top: 1, height: 1, background: '#d1d5db', zIndex: 1 }} />
    </div>
  </div>
);
```

### 1-1. `WrittenBy` (slideLayout 표 17 + 텍스트 개체 틀 18)

Source of truth: the source weekly PPT layout. A 1×2 native table at x 1323 / y 49, 352 × 41
(label col 125, name col 227), **every edge 1pt solid black (`tx1`) → `2px solid #000000`**, label cell `#f2f2f2`
(bg1 lumMod 95%), name cell white, Arial 10pt → 20px, **regular weight (not bold)**, left-aligned.
Do not use a gray border or a bold label. In PPT-geometry decks (absolute layout copied from the source PPT)
pass `style={{ position: 'absolute', left: 1323, top: 49 }}`; in the flow `MasterHeader` above it sits in the right cluster.

```tsx
const line = '2px solid #000000';

export const WrittenBy = ({ researcher, style }: { researcher: string; style?: React.CSSProperties }) => (
  <table style={{ ...style, width: 352, height: 41, borderCollapse: 'collapse', tableLayout: 'fixed', fontFamily: 'Arial, "Malgun Gothic", sans-serif', fontSize: 20, fontWeight: 400, lineHeight: 1.2, color: '#000000', flex: 'none' }}>
    <colgroup><col style={{ width: 125 }} /><col style={{ width: 227 }} /></colgroup>
    <tbody>
      <tr>
        <td style={{ border: line, background: '#f2f2f2', padding: '0 4px 0 8px', whiteSpace: 'nowrap' }}>Written by</td>
        <td style={{ border: line, background: '#ffffff', padding: '0 14px', whiteSpace: 'nowrap' }}>{researcher}</td>
      </tr>
    </tbody>
  </table>
);
```

### 2. `TopHeaderTable` (Slide 6 Standard Content Tracker)

Geometry is the source PPT's (1pt = 2px on the 1920 canvas), positioned absolutely under the master header.
Source of truth for the line/fill spec: the source weekly PPT (표 5).

- **Grid: every cell edge is 1pt solid black (`tx1`, some edges `tx1` lumMod 85% — still black) → `2px solid #000000`.**
  Not a gray hairline.
- Header rows 1–2 (incl. the M–F date row and the blank status column) fill `#f2f2f2`; text Arial 7pt → 14px, regular.
- Date row (row 2) is vertically **centered** (`anchor="ctr"`), not bottom-aligned.
- Body row: the five M–F cells fill `#a6a6a6` (bg1 lumMod 65%); every other body cell is white / no fill.

```tsx
const line = '2px solid #000000';
const hd: React.CSSProperties = { border: line, background: '#f2f2f2', padding: '2px 6px', textAlign: 'center', verticalAlign: 'middle' };
const bd: React.CSSProperties = { border: line, padding: '4px 10px', background: '#ffffff', verticalAlign: 'middle' };
const day: React.CSSProperties = { border: line, background: '#a6a6a6' };

export const TopHeaderTable = ({
  project, expNo, studyTitle, specificAim, issuePlan, researcher,
  dates = ['14', '15', '16', '17', '18'],
}: {
  project: string; expNo: string; studyTitle: string; specificAim: string;
  issuePlan?: string; researcher: string; dates?: [string, string, string, string, string];
}) => (
  <table style={{ position: 'absolute', left: 44, top: 135, width: 1831, borderCollapse: 'collapse', tableLayout: 'fixed', fontFamily: 'Arial, "Malgun Gothic", sans-serif', fontSize: 14, lineHeight: 1.2, color: '#000000' }}>
    <colgroup>
      <col style={{ width: 83 }} /><col style={{ width: 114 }} /><col style={{ width: 335 }} /><col style={{ width: 490 }} />
      <col style={{ width: 47 }} /><col style={{ width: 47 }} /><col style={{ width: 47 }} /><col style={{ width: 47 }} /><col style={{ width: 47 }} />
      <col style={{ width: 34 }} /><col style={{ width: 420 }} /><col style={{ width: 119 }} />
    </colgroup>
    <tbody>
      <tr style={{ height: 26 }}>
        <td rowSpan={2} style={hd}>Project</td>
        <td rowSpan={2} style={hd}>Exp No.</td>
        <td rowSpan={2} style={hd}>Study Title</td>
        <td rowSpan={2} style={hd}>Specific Aim</td>
        <td style={hd}>M</td><td style={hd}>T</td><td style={hd}>W</td><td style={hd}>T</td><td style={hd}>F</td>
        <td rowSpan={2} style={hd} />
        <td rowSpan={2} style={hd}>Issue / Plan</td>
        <td rowSpan={2} style={hd}>Researcher</td>
      </tr>
      <tr style={{ height: 33 }}>
        <td style={hd}>{dates[0]}</td>
        <td style={hd}>{dates[1]}</td>
        <td style={hd}>{dates[2]}</td>
        <td style={hd}>{dates[3]}</td>
        <td style={hd}>{dates[4]}</td>
      </tr>
      <tr style={{ height: 30 }}>
        <td style={{ ...bd, textAlign: 'center' }}>{project}</td>
        <td style={{ ...bd, textAlign: 'center' }}>{expNo}</td>
        <td style={bd}>{studyTitle}</td>
        <td style={bd}>{specificAim}</td>
        <td style={day} /><td style={day} /><td style={day} /><td style={day} /><td style={day} />
        <td style={bd} />
        <td style={bd}>{issuePlan}</td>
        <td style={{ ...bd, textAlign: 'center' }}>{researcher}</td>
      </tr>
    </tbody>
  </table>
);
```

## Tables & PowerPoint export

Anything that is a table in the source deck — project summary, status tables, report lists, QC schedules,
key/value inventories, the tracker, even the "Written by" box — **must be authored as a real `<table>`**:

- `<table style={{ borderCollapse: 'collapse', tableLayout: 'fixed' }}>` + a `<colgroup>` with px (or %) widths, explicit row heights.
- Merge with `rowSpan` / `colSpan`; never fake a table with `display: grid`, flex rows, or absolutely positioned boxes.
- Put fills, borders, padding and vertical alignment on the `<td>`/`<th>` (not on wrapper divs), one `<td>` per visual cell.
- Leave headroom in tight `whiteSpace: 'nowrap'` cells: PowerPoint's glyphs run slightly wider than Chrome's, so a label that just fits in the browser wraps in the PPTX.

open-slide's built-in "Export as PPTX" (`@open-slide/core` 2.x) has no table primitive and draws every cell as a
rectangle + text box. To get native, editable PowerPoint tables, post-process the export:

1. Export the deck from the viewer (Export → PPTX).
2. With the deck open at `/s/<slide-id>`, paste `scripts/extract-tables.js` into the browser console. It starts from page 1, walks every page until the last one and downloads `tables.json` (no page count to set).
3. `python3 scripts/pptx-native-tables.py <export>.pptx tables.json "<name> (표 적용).pptx"` — removes the per-cell shapes inside each table area and inserts `<a:tbl>` tables with the same widths, heights, merges, fills, borders, margins and text runs.
