import React from 'react';
import { 
  FileText, 
  BookOpen, 
  Gavel, 
  CheckSquare, 
  AlertTriangle, 
  ShieldAlert, 
  ShieldCheck, 
  Award,
  ChevronRight,
  Download,
  MessageSquare,
  Activity,
  Clock
} from 'lucide-react';

const SECTIONS = [
  { id: 'overview', label: 'Case Overview', icon: FileText, desc: 'Summary, facts & claims' },
  { id: 'law', label: 'Law', icon: BookOpen, desc: 'Acts, sections & provisos' },
  { id: 'precedents', label: 'Precedents', icon: Gavel, desc: 'Supreme Court rulings' },
  { id: 'evidence', label: 'Evidence', icon: CheckSquare, desc: 'Proof, gaps & weaknesses' },
  { id: 'constraints', label: 'Constraints', icon: AlertTriangle, desc: 'Procedural bars & limits' },
  { id: 'opposition', label: 'Opposition', icon: ShieldAlert, desc: 'Adversarial counterarguments' },
  { id: 'audit', label: 'Audit', icon: ShieldCheck, desc: 'Citation validation & status' },
  { id: 'final', label: 'Final Assessment', icon: Award, desc: 'Assessment & probable outcome' },
  { id: 'observability', label: 'Observability & Trace', icon: Activity, desc: 'Telemetry, metrics & agent trace' }
];

export default function WorkspaceSidebar({ 
  activeSection, 
  onSelectSection, 
  analysisData, 
  onDownloadPdf,
  onOpenHistory
}) {
  const outcome = analysisData?.outcome || 'PASS';
  const lawCount = analysisData?.agent_outputs?.law_sections?.length || 0;
  const precedentCount = analysisData?.agent_outputs?.precedents?.length || 0;
  const constraintCount = (analysisData?.agent_outputs?.procedural_constraints?.length || 0) + (analysisData?.agent_outputs?.substantive_constraints?.length || 0);

  return (
    <aside className="workspace-sidebar">
      {/* Sidebar Header: "Case Analysis" */}
      <div style={{
        padding: '1.25rem 1.25rem 1rem 1.25rem',
        borderBottom: '1px solid var(--court-parchment-border)'
      }}>
        <div style={{
          fontSize: '11px',
          textTransform: 'uppercase',
          letterSpacing: '0.04em',
          color: 'var(--ink-muted)',
          marginBottom: '0.3rem',
          fontWeight: 600
        }}>
          CASE ANALYSIS WORKSPACE
        </div>
        <h3 style={{
          fontSize: '1.25rem',
          color: 'var(--court-navy)',
          fontWeight: 700
        }}>
          Case Analysis
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.4rem' }}>
          <span className={`badge-pill ${outcome === 'PASS' ? 'badge-pass' : outcome === 'RECOVERED' ? 'badge-warn' : 'badge-alert'}`}>
            AUDIT: {outcome}
          </span>
          <span style={{ fontSize: '11.5px', color: 'var(--ink-muted)' }}>
            {analysisData?.elapsed_seconds ? `${analysisData.elapsed_seconds}s` : 'Verified'}
          </span>
        </div>
      </div>

      {/* Navigation Sections */}
      <nav style={{ flex: 1, padding: '0.5rem 0' }}>
        {SECTIONS.map((sec) => {
          const Icon = sec.icon;
          const isActive = activeSection === sec.id;

          let badgeText = null;
          if (sec.id === 'law' && lawCount > 0) badgeText = `${lawCount} Sec`;
          if (sec.id === 'precedents' && precedentCount > 0) badgeText = `${precedentCount} SC`;
          if (sec.id === 'constraints' && constraintCount > 0) badgeText = `${constraintCount} Bars`;
          if (sec.id === 'observability') badgeText = 'Live Trace';
          if (sec.id === 'chat') badgeText = 'Live';

          return (
            <button
              key={sec.id}
              onClick={() => onSelectSection(sec.id)}
              className={`sidebar-tab-btn ${isActive ? 'active' : ''}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Icon size={16} color={isActive ? 'var(--court-navy)' : 'var(--ink-muted)'} />
                <div>
                  <div style={{ fontSize: '14px', color: isActive ? 'var(--court-navy)' : 'var(--ink-primary)' }}>
                    {sec.label}
                  </div>
                  <div style={{ fontSize: '11.5px', color: 'var(--ink-muted)', fontWeight: 400 }}>
                    {sec.desc}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                {badgeText && (
                  <span className={`badge-pill ${sec.id === 'chat' ? 'badge-pass' : 'badge-gold'}`} style={{ fontSize: '10px', padding: '1px 5px' }}>
                    {badgeText}
                  </span>
                )}
                <ChevronRight size={14} color={isActive ? 'var(--court-navy)' : '#cbd5e0'} />
              </div>
            </button>
          );
        })}
      </nav>

      {/* Sidebar Footer with PDF export & history buttons */}
      <div style={{
        padding: '1rem 1.25rem',
        borderTop: '1px solid var(--court-parchment-border)',
        background: 'var(--court-parchment-subtle)',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        {onOpenHistory && (
          <button
            onClick={onOpenHistory}
            className="btn-legal-secondary"
            style={{ width: '100%', fontSize: '12.5px', padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
          >
            <Clock size={14} /> Search & Case History
          </button>
        )}
        <button
          onClick={onDownloadPdf}
          className="btn-legal-gold"
          style={{ width: '100%', fontSize: '12.5px', padding: '0.6rem 1rem' }}
        >
          <Download size={14} /> Download PDF Brief
        </button>
        <div style={{
          textAlign: 'center',
          fontSize: '11px',
          color: 'var(--ink-muted)',
          marginTop: '0.4rem'
        }}>
          Court-Ready Assessment Report
        </div>
      </div>
    </aside>
  );
}
