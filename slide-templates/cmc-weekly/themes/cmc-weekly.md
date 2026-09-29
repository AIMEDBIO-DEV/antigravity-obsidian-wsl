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
   - **우측 상단**: 회사 공식 로고 (`image2.png` / `image3.png`) 및 담당 연구원 표기
2. **Slide 1: Cover Archetype** — Crisp white canvas, middle hero graphic banner (`top: 175px`, `height: 728px`) with translucent white tint (84%), fixed left title group (`CMC REGULAR PROGRESS REPORT` category + `Weekly Progress <dates>` only, with no subtitle or extra widgets), and a vertical translucent Crimson Red rectangle (`#C00000`, 88% opacity) on the right containing centered "CMC Team" and the company logo in the bottom right corner.
3. **Slide 2: Table of Contents / Executive Summary Archetype** — Grouped by project tags (`[P001]`, `[P002]`, `[P003]`, `[P-EX]`), with structured 4-column tables: `EXP-No. | EXP title | 신규 추가된 내용 | 담당자`. Header row filled with Crimson Red (`#C00000`) and white text.
4. **Slide 6: Universal Content Slide Archetype** — Fixed `MasterHeader` + `TopHeaderTable` across the top of all content slides (neutral light-gray `#F2F2F2` header, M-T-W-T-F active day indicators, status dot, researcher), followed by the content area.
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

## Paste-Ready Components

### 1. `MasterHeader` (SlideLayout13 / SlideLayout15 Top Header)

```tsx
import companyLogoRed from '@assets/image3.png';

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
        height: 36,
      }}
    >
      {/* Left: Document Title / Date range */}
      <div style={{ fontSize: 18, fontWeight: 800, color: '#111827', letterSpacing: '-0.01em', whiteSpace: 'nowrap' }}>
        {title}
      </div>

      {/* Right Cluster: Status Legend shifted next to Written by Table & Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* 3-State Status Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, fontWeight: 600, whiteSpace: 'nowrap' }}>
          <span style={{ color: '#68a490' }}>● 계획대로 진행중</span>
          <span style={{ color: '#9ca3af' }}>/</span>
          <span style={{ color: '#eac282' }}>● Minor 사항 있음</span>
          <span style={{ color: '#9ca3af' }}>/</span>
          <span style={{ color: '#d65532' }}>● 큰 issue 있음</span>
        </div>

        {/* Divider */}
        <div style={{ width: 1, height: 20, background: '#d1d5db', margin: '0 4px' }} />

        {/* Written by Table */}
        <table style={{ borderCollapse: 'collapse', border: '1px solid #4b5563', height: 26, fontSize: 12 }}>
          <tbody>
            <tr>
              <td style={{ background: '#f2f2f2', border: '1px solid #4b5563', padding: '2px 12px', fontWeight: 700, color: '#111827', whiteSpace: 'nowrap' }}>
                Written by
              </td>
              <td style={{ background: '#ffffff', border: '1px solid #4b5563', padding: '2px 16px', fontWeight: 600, color: '#111827', minWidth: 90, textAlign: 'center', whiteSpace: 'nowrap' }}>
                {researcher}
              </td>
            </tr>
          </tbody>
        </table>

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

### 2. `TopHeaderTable` (Slide 6 Standard Content Tracker)

```tsx
// Table row 1 includes dates (M-T-W-T-F) with individual bordered divider cells to Researcher.
// Table row 2 shades ALL 5 date cells in gray (#9ca3af, NOT crimson) per corporate standard.
```
