import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  Loader2, 
  BookOpen, 
  Gavel, 
  FileCheck, 
  Lock, 
  Swords, 
  ShieldCheck, 
  Award,
  FileText
} from 'lucide-react';

const STAGES = [
  { id: 1, name: 'Case Understanding', desc: 'Parsing facts, timeline, parties and claims', icon: FileText },
  { id: 2, name: 'Law Analysis', desc: 'Retrieving statutory sections from 12 Central Acts', icon: BookOpen },
  { id: 3, name: 'Precedent Research', desc: 'Matching Supreme Court ratios and citations', icon: Gavel },
  { id: 4, name: 'Evidence Assessment', desc: 'Auditing proof matrix, gaps and weaknesses', icon: FileCheck },
  { id: 5, name: 'Constraint Analysis', desc: 'Detecting cooling-off bars and provisos', icon: Lock },
  { id: 6, name: 'Opposition Analysis', desc: 'Formulating adversarial objections', icon: Swords },
  { id: 7, name: 'Audit', desc: 'Verifying citations and statutory integrity', icon: ShieldCheck },
  { id: 8, name: 'Final Assessment', desc: 'Synthesizing structured assessment brief', icon: Award }
];

export default function AgentProgressModal({ active }) {
  const [currentStageIdx, setCurrentStageIdx] = useState(0);

  useEffect(() => {
    if (!active) {
      setCurrentStageIdx(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentStageIdx((prev) => {
        if (prev < STAGES.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 450);

    return () => clearInterval(interval);
  }, [active]);

  if (!active) return null;

  return (
    <div className="agent-progress-overlay">
      <div className="agent-progress-modal">
        {/* Header */}
        <div style={{
          background: 'var(--court-navy)',
          padding: '1.1rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          color: '#ffffff'
        }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', color: '#ffffff', fontWeight: 700 }}>
              JurisAI Analysis Pipeline
            </h3>
            <div style={{ fontSize: '12px', color: 'var(--court-gold-light)', marginTop: '2px' }}>
              Processing Stage {currentStageIdx + 1} of 8
            </div>
          </div>
          <span className="badge-pill badge-gold" style={{ fontSize: '11px' }}>
            ANALYSIS IN PROGRESS
          </span>
        </div>

        {/* Progress Stages List */}
        <div style={{ padding: '1.25rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
          {STAGES.map((stg, idx) => {
            const isCompleted = idx < currentStageIdx;
            const isCurrent = idx === currentStageIdx;
            const Icon = stg.icon;

            return (
              <div
                key={stg.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.85rem',
                  padding: '0.6rem 0.85rem',
                  borderRadius: '4px',
                  backgroundColor: isCurrent ? 'var(--court-parchment-subtle)' : isCompleted ? '#ffffff' : 'transparent',
                  border: isCurrent ? '1px solid var(--court-gold)' : isCompleted ? '1px solid #e2e8f0' : '1px solid transparent'
                }}
              >
                {/* Status Icon */}
                <div style={{ width: '22px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {isCompleted ? (
                    <CheckCircle2 size={18} color="var(--status-pass)" />
                  ) : isCurrent ? (
                    <Loader2 size={18} color="var(--court-gold-dark)" className="pulsing-indicator" />
                  ) : (
                    <div style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: '#cbd5e0'
                    }} />
                  )}
                </div>

                {/* Stage Info */}
                <div style={{ flex: 1 }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontWeight: isCurrent ? 700 : isCompleted ? 600 : 400,
                    fontSize: '13.5px',
                    color: isCurrent ? 'var(--court-navy)' : isCompleted ? 'var(--ink-primary)' : 'var(--ink-faint)'
                  }}>
                    <Icon size={14} color={isCurrent ? 'var(--court-gold-dark)' : isCompleted ? 'var(--status-pass)' : '#a0aec0'} />
                    <span>{stg.name}</span>
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: isCurrent ? 'var(--ink-secondary)' : isCompleted ? 'var(--ink-muted)' : 'var(--ink-faint)',
                    marginTop: '1px'
                  }}>
                    {stg.desc}
                  </div>
                </div>

                {/* Step pill */}
                <div>
                  <span style={{
                    fontSize: '11px',
                    color: isCompleted ? 'var(--status-pass)' : isCurrent ? 'var(--court-gold-dark)' : 'var(--ink-faint)',
                    fontWeight: 600
                  }}>
                    {isCompleted ? 'COMPLETED' : isCurrent ? 'PROCESSING' : 'PENDING'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer info bar */}
        <div style={{
          background: 'var(--court-parchment-subtle)',
          padding: '0.75rem 1.5rem',
          borderTop: '1px solid var(--court-parchment-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          color: 'var(--ink-muted)'
        }}>
          <span>Searching 916 chunks in ChromaDB</span>
          <span>FastEmbed BGE-Small</span>
        </div>
      </div>
    </div>
  );
}
