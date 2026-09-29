import React from 'react';
import type { Page } from '@open-slide/core';
import { useSlidePageNumber } from '@open-slide/core';

import bgBanner from '../assets/image1.png';
import companyLogoWhite from '../assets/image2.png';
import companyLogoRed from '../assets/image3.png';

const pageFill: React.CSSProperties = {
  width: '100%',
  height: '100%',
  boxSizing: 'border-box',
  background: '#ffffff',
  color: '#111827',
  fontFamily: 'Pretendard, "Malgun Gothic", "맑은 고딕", -apple-system, sans-serif',
  position: 'relative',
  padding: '24px 44px 36px 44px',
};

const Footer = () => {
  const { current, total } = useSlidePageNumber();
  return (
    <div
      style={{
        position: 'absolute',
        left: 44,
        right: 44,
        bottom: 14,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: 13,
        color: '#6b7280',
        fontWeight: 600,
      }}
    >
      <span>CMC team</span>
      <span>
        {current} / {total}
      </span>
    </div>
  );
};

// -------------------------------------------------------------
// Common Master Header (SlideLayout13 / SlideLayout15 Top Header)
// -------------------------------------------------------------
const MasterHeader = ({
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
      <div
        style={{
          fontSize: 18,
          fontWeight: 800,
          color: '#111827',
          letterSpacing: '-0.01em',
          whiteSpace: 'nowrap',
        }}
      >
        {title}
      </div>

      {/* Right Cluster: Status Legend shifted next to Written by Table & Logo */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 16,
        }}
      >
        {/* 3-State Status Legend */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: 12,
            fontWeight: 600,
            whiteSpace: 'nowrap',
          }}
        >
          <span style={{ color: '#68a490' }}>● 계획대로 진행중</span>
          <span style={{ color: '#9ca3af' }}>/</span>
          <span style={{ color: '#eac282' }}>● Minor 사항 있음</span>
          <span style={{ color: '#9ca3af' }}>/</span>
          <span style={{ color: '#d65532' }}>● 큰 issue 있음</span>
        </div>

        {/* Vertical divider */}
        <div style={{ width: 1, height: 20, background: '#d1d5db', margin: '0 4px' }} />

        {/* Written by Table */}
        <table
          style={{
            borderCollapse: 'collapse',
            border: '1px solid #4b5563',
            height: 26,
            fontSize: 12,
          }}
        >
          <tbody>
            <tr>
              <td
                style={{
                  background: '#f2f2f2',
                  border: '1px solid #4b5563',
                  padding: '2px 12px',
                  fontWeight: 700,
                  color: '#111827',
                  whiteSpace: 'nowrap',
                }}
              >
                Written by
              </td>
              <td
                style={{
                  background: '#ffffff',
                  border: '1px solid #4b5563',
                  padding: '2px 16px',
                  fontWeight: 600,
                  color: '#111827',
                  minWidth: 90,
                  textAlign: 'center',
                  whiteSpace: 'nowrap',
                }}
              >
                {researcher}
              </td>
            </tr>
          </tbody>
        </table>

        {/* Official Red Company Logo for light backgrounds */}
        <img
          src={companyLogoRed}
          alt="AimedBio Logo"
          style={{
            height: 24,
            maxWidth: 140,
            objectFit: 'contain',
            display: 'block',
          }}
        />
      </div>
    </div>

    {/* Master Header Bottom Rule: Crimson red accent bar on left + Gray line across */}
    <div style={{ position: 'relative', width: '100%', height: 3, marginTop: 6 }}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: 70,
          height: 3,
          background: '#c00000',
          zIndex: 2,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 1,
          height: 1,
          background: '#d1d5db',
          zIndex: 1,
        }}
      />
    </div>
  </div>
);

// -------------------------------------------------------------
// 1. Cover Archetype (Slide 1 exact replica)
// -------------------------------------------------------------
const DemoCover: Page = () => (
  <div style={{ ...pageFill, padding: 0, overflow: 'hidden' }}>
    {/* Middle Banner with 84% translucent white tint */}
    <div style={{ position: 'absolute', left: 0, top: 175, width: 1920, height: 728, overflow: 'hidden' }}>
      <img
        src={bgBanner}
        alt="Background Banner"
        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(255, 255, 255, 0.84)',
        }}
      />
    </div>

    {/* Title on the Left */}
    <div
      style={{
        position: 'absolute',
        left: 172,
        top: 414,
        width: 700,
        zIndex: 5,
      }}
    >
      <div
        style={{
          fontSize: 16,
          fontWeight: 800,
          color: '#c00000',
          letterSpacing: '0.08em',
          marginBottom: 12,
        }}
      >
        CMC REGULAR PROGRESS REPORT
      </div>
      <h1
        style={{
          fontSize: 54,
          fontWeight: 800,
          color: '#111827',
          lineHeight: 1.15,
          margin: 0,
          letterSpacing: '-0.02em',
        }}
      >
        Weekly Progress 260101~260105
      </h1>
    </div>

    {/* Crimson Red Translucent Card on the Right */}
    <div
      style={{
        position: 'absolute',
        left: 978,
        top: 105,
        width: 773,
        height: 870,
        background: 'rgba(192, 0, 0, 0.88)',
        zIndex: 10,
        boxSizing: 'border-box',
        padding: '60px 70px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
      }}
    >
      <h2
        style={{
          fontSize: 54,
          fontWeight: 800,
          color: '#ffffff',
          margin: 0,
          letterSpacing: '-0.01em',
        }}
      >
        CMC Team
      </h2>

      <div
        style={{
          position: 'absolute',
          bottom: 50,
          right: 60,
        }}
      >
        <img
          src={companyLogoWhite}
          alt="Company Logo"
          style={{
            height: 48,
            maxWidth: 240,
            objectFit: 'contain',
          }}
        />
      </div>
    </div>
  </div>
);

// -------------------------------------------------------------
// 2. Table of Contents / Executive Summary Archetype (Slide 2 exact replica)
// -------------------------------------------------------------
const DemoAgenda: Page = () => (
  <div style={pageFill}>
    {/* Master Header */}
    <MasterHeader title="[CMC] Weekly Progress 260101–260105" />

    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 16,
        borderBottom: '2px solid #111827',
        paddingBottom: 8,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <h2 style={{ fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>
          목차 및 주간 주요 업데이트 요약 (Table of Contents & Highlights)
        </h2>
        <span style={{ fontSize: 13, background: '#c00000', color: '#fff', fontWeight: 700, padding: '2px 8px', borderRadius: 3 }}>
          Executive Overview
        </span>
      </div>
      <span style={{ fontSize: 14, fontWeight: 700, color: '#c00000' }}>CMC team</span>
    </div>

    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* P001 */}
      <div>
        <div style={{ fontSize: 15, fontWeight: 800, color: '#c00000', marginBottom: 4 }}>
          [P001]
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#c00000', color: '#ffffff', height: 26 }}>
              <th style={{ width: '8%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'center' }}>EXP-No.</th>
              <th style={{ width: '25%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'left' }}>EXP title</th>
              <th style={{ width: '53%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'left' }}>신규 추가된 내용</th>
              <th style={{ width: '14%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'center' }}>담당자</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ height: 32, background: '#ffffff' }}>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', fontWeight: 600 }}>-</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px', fontWeight: 700 }}>CRO Management_Vendor A</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px' }}>
                예시 문구: 인증서 사본 수령 및 공유. 안정성 시험 재시험 진행 중. 근거 문서 확보.
              </td>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center' }}>담당자 A / B / C</td>
            </tr>
            <tr style={{ height: 32, background: '#f9fafb' }}>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', fontWeight: 600 }}>-</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px', fontWeight: 700 }}>CRO Management_Vendor B_Sample-01</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px' }}>
                예시 문구: 시험 항목 재평가 완료. 프로토콜 개정 2판 작성. 문서 초안 검토 중.
              </td>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center' }}>담당자 A / B / C</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* P002 */}
      <div>
        <div style={{ fontSize: 15, fontWeight: 800, color: '#c00000', marginBottom: 4 }}>
          [P002]
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#c00000', color: '#ffffff', height: 26 }}>
              <th style={{ width: '8%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'center' }}>EXP-No.</th>
              <th style={{ width: '25%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'left' }}>EXP title</th>
              <th style={{ width: '53%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'left' }}>신규 추가된 내용</th>
              <th style={{ width: '14%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'center' }}>담당자</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ height: 32, background: '#ffffff' }}>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', fontWeight: 600 }}>-</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px', fontWeight: 700 }}>CRO Management_Vendor C_Sample-02</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px' }}>
                예시 문구: 재공급 진행 중. 장기 안정성 시험 진행 중. 배송 상태 추적.
              </td>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center' }}>담당자 B / A / C</td>
            </tr>
            <tr style={{ height: 32, background: '#f9fafb' }}>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', fontWeight: 600 }}>-</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px', fontWeight: 700 }}>Global Submission</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px' }}>
                예시 문구: 국가별 제출 진행 중. 시험 데이터 업로드.
              </td>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center' }}>CMC 전체</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* P003 */}
      <div>
        <div style={{ fontSize: 15, fontWeight: 800, color: '#c00000', marginBottom: 4 }}>
          [P003]
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#c00000', color: '#ffffff', height: 26 }}>
              <th style={{ width: '8%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'center' }}>EXP-No.</th>
              <th style={{ width: '25%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'left' }}>EXP title</th>
              <th style={{ width: '53%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'left' }}>신규 추가된 내용</th>
              <th style={{ width: '14%', border: '1px solid #b91c1c', padding: '3px 6px', textAlign: 'center' }}>담당자</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ height: 32, background: '#ffffff' }}>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', fontWeight: 600 }}>-</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px', fontWeight: 700 }}>CRO Management_Vendor C_Sample-03</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px' }}>
                예시 문구: 계약 발효. 청구서 예정. 데이터 수령 후 전략 결정.
              </td>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center' }}>담당자 B / A / C</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Footer />
  </div>
);

// -------------------------------------------------------------
// 3. Body Archetype (Slide 6 exact replica)
// -------------------------------------------------------------
type HeaderProps = {
  project: string;
  expNo: string;
  studyTitle: string;
  specificAim: string;
  dates?: [string, string, string, string, string];
  activeDays?: [boolean, boolean, boolean, boolean, boolean];
  statusColor?: string;
  issuePlan: string;
  researcher: string;
};

const TopHeaderTable = ({
  project,
  expNo,
  studyTitle,
  specificAim,
  dates = ['14', '15', '16', '17', '18'],
  activeDays = [false, true, true, false, false],
  statusColor = '#16a34a',
  issuePlan,
  researcher,
}: HeaderProps) => (
  <div style={{ width: '100%', marginBottom: 12 }}>
    <table
      style={{
        width: '100%',
        borderCollapse: 'collapse',
        fontSize: 12,
        textAlign: 'center',
        border: '1px solid #4b5563',
      }}
    >
      <thead>
        <tr style={{ background: '#f2f2f2', color: '#111827', height: 26 }}>
          <th style={{ width: '6%', border: '1px solid #6b7280', padding: '3px 4px' }}>Project</th>
          <th style={{ width: '8%', border: '1px solid #6b7280', padding: '3px 4px' }}>Exp No.</th>
          <th style={{ width: '22%', border: '1px solid #6b7280', padding: '3px 4px' }}>Study Title</th>
          <th style={{ width: '26%', border: '1px solid #6b7280', padding: '3px 4px' }}>Specific Aim</th>
          <th style={{ width: '2.5%', border: '1px solid #6b7280' }}>M</th>
          <th style={{ width: '2.5%', border: '1px solid #6b7280' }}>T</th>
          <th style={{ width: '2.5%', border: '1px solid #6b7280' }}>W</th>
          <th style={{ width: '2.5%', border: '1px solid #6b7280' }}>T</th>
          <th style={{ width: '2.5%', border: '1px solid #6b7280' }}>F</th>
          <th style={{ width: '2%', border: '1px solid #6b7280' }}>●</th>
          <th style={{ width: '18%', border: '1px solid #6b7280', padding: '3px 4px' }}>Issue / Plan</th>
          <th style={{ width: '8%', border: '1px solid #6b7280', padding: '3px 4px' }}>Researcher</th>
        </tr>
        <tr style={{ background: '#f9fafb', color: '#374151', height: 18, fontSize: 11 }}>
          <td colSpan={4} style={{ border: '1px solid #d1d5db' }} />
          <td style={{ border: '1px solid #d1d5db', fontWeight: 700 }}>{dates[0]}</td>
          <td style={{ border: '1px solid #d1d5db', fontWeight: 700 }}>{dates[1]}</td>
          <td style={{ border: '1px solid #d1d5db', fontWeight: 700 }}>{dates[2]}</td>
          <td style={{ border: '1px solid #d1d5db', fontWeight: 700 }}>{dates[3]}</td>
          <td style={{ border: '1px solid #d1d5db', fontWeight: 700 }}>{dates[4]}</td>
          <td style={{ border: '1px solid #d1d5db' }} />
          <td style={{ border: '1px solid #d1d5db' }} />
          <td style={{ border: '1px solid #d1d5db' }} />
        </tr>
      </thead>
      <tbody>
        <tr style={{ height: 28, background: '#ffffff', color: '#111827' }}>
          <td style={{ border: '1px solid #d1d5db', fontWeight: 800, color: '#c00000' }}>{project}</td>
          <td style={{ border: '1px solid #d1d5db', fontWeight: 700 }}>{expNo}</td>
          <td style={{ border: '1px solid #d1d5db', textAlign: 'left', padding: '3px 8px', fontWeight: 600 }}>{studyTitle}</td>
          <td style={{ border: '1px solid #d1d5db', textAlign: 'left', padding: '3px 8px', fontSize: 11 }}>{specificAim}</td>
          {/* 5-day schedule cells shaded in gray (not crimson) */}
          <td style={{ border: '1px solid #d1d5db', background: '#9ca3af' }} />
          <td style={{ border: '1px solid #d1d5db', background: '#9ca3af' }} />
          <td style={{ border: '1px solid #d1d5db', background: '#9ca3af' }} />
          <td style={{ border: '1px solid #d1d5db', background: '#9ca3af' }} />
          <td style={{ border: '1px solid #d1d5db', background: '#9ca3af' }} />
          <td style={{ border: '1px solid #d1d5db' }}>
            <span style={{ color: statusColor, fontSize: 14 }}>●</span>
          </td>
          <td style={{ border: '1px solid #d1d5db', textAlign: 'left', padding: '3px 8px', fontSize: 11 }}>{issuePlan}</td>
          <td style={{ border: '1px solid #d1d5db', fontWeight: 600, fontSize: 11 }}>{researcher}</td>
        </tr>
      </tbody>
    </table>
  </div>
);

const DemoBody: Page = () => (
  <div style={pageFill}>
    {/* Master Header */}
    <MasterHeader
      title="[CMC] Weekly Progress 260101–260105"
      researcher="담당자 C / A"
    />

    <TopHeaderTable
      project="P001"
      expNo="-EXP001"
      studyTitle="CRO Management_Vendor A"
      specificAim="Report finalization & document drafting (example)"
      issuePlan="Finalize sample report & submit first batch (example)"
      researcher="담당자 C / A"
      dates={['14', '15', '16', '17', '18']}
      activeDays={[false, true, true, false, false]}
      statusColor="#16a34a"
    />

    <div style={{ marginBottom: 12 }}>
      <h3 style={{ fontSize: 26, fontWeight: 800, color: '#111827', margin: 0 }}>
        Submission timeline (example – 4 months)
      </h3>
      <div style={{ fontSize: 15, fontWeight: 700, color: '#c00000', marginTop: 3 }}>
        Source document status & preparation checklist
      </div>
    </div>

    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, height: 690 }}>
      {/* Product A Source Documents */}
      <div>
        <div style={{ fontSize: 16, fontWeight: 800, color: '#111827', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 4, height: 16, background: '#c00000', display: 'inline-block' }} />
          <span>Product A Source document status (Total 2 reports)</span>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#f2f2f2', color: '#111827', height: 26 }}>
              <th style={{ width: '20%', border: '1px solid #6b7280', padding: '4px' }}>Category</th>
              <th style={{ width: '55%', border: '1px solid #6b7280', padding: '4px' }}>Report</th>
              <th style={{ width: '25%', border: '1px solid #6b7280', padding: '4px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ height: 32, background: '#ffffff' }}>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', fontWeight: 700 }}>Prod A</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px' }}>Sample study Report</td>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', color: '#c00000', fontWeight: 700 }}>3rd review on-going</td>
            </tr>
            <tr style={{ height: 32, background: '#f9fafb' }}>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', fontWeight: 700 }}>Prod A</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px' }}>Characterization Report</td>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', color: '#16a34a', fontWeight: 700 }}>Review completed</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Product B Source Documents */}
      <div>
        <div style={{ fontSize: 16, fontWeight: 800, color: '#111827', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 4, height: 16, background: '#c00000', display: 'inline-block' }} />
          <span>Product B Source document status (Total 1 report)</span>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#f2f2f2', color: '#111827', height: 26 }}>
              <th style={{ width: '20%', border: '1px solid #6b7280', padding: '4px' }}>Category</th>
              <th style={{ width: '55%', border: '1px solid #6b7280', padding: '4px' }}>Report</th>
              <th style={{ width: '25%', border: '1px solid #6b7280', padding: '4px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ height: 32, background: '#ffffff' }}>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', fontWeight: 700 }}>Prod B</td>
              <td style={{ border: '1px solid #d1d5db', padding: '4px 8px' }}>Method Qualification Report_Sample</td>
              <td style={{ border: '1px solid #d1d5db', textAlign: 'center', color: '#16a34a', fontWeight: 700 }}>Completed</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Footer />
  </div>
);

export default [DemoCover, DemoAgenda, DemoBody] satisfies Page[];
