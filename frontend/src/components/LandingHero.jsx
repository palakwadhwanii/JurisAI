import React from 'react';
import { 
  ShieldAlert, 
  ArrowDown, 
  BookOpen, 
  Gavel, 
  FileCheck, 
  Lock, 
  Swords, 
  FileText,
  HelpCircle,
  Download,
  Scale,
  Activity,
  Cpu
} from 'lucide-react';

export default function LandingHero({ onScrollToInput }) {
  return (
    <div className="landing-container">
      {/* 1. Hero Section */}
      <section style={{
        background: 'linear-gradient(180deg, #ffffff 0%, var(--court-parchment) 100%)',
        borderBottom: '1px solid var(--court-parchment-border)',
        padding: '5rem 1.5rem 4.5rem 1.5rem',
        textAlign: 'center',
        position: 'relative'
      }}>
        <div style={{ maxWidth: '840px', margin: '0 auto' }}>
          {/* Subtle minimal legal pill */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '5px 14px',
            backgroundColor: '#f9f6ed',
            border: '1px solid #ebd7af',
            borderRadius: '20px',
            marginBottom: '1.5rem'
          }}>
            <Scale size={14} color="var(--court-gold-dark)" />
            <span style={{
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--court-gold-dark)',
              letterSpacing: '0.04em'
            }}>
              INDIAN FAMILY LAW RESEARCH PLATFORM
            </span>
          </div>

          {/* Prominent Title & Subtitle */}
          <h1 style={{
            fontSize: '3.6rem',
            fontWeight: 700,
            color: 'var(--court-navy)',
            lineHeight: 1.1,
            marginBottom: '0.85rem',
            letterSpacing: '-0.02em'
          }}>
            JurisAI
          </h1>

          <h2 style={{
            fontSize: '1.45rem',
            fontWeight: 600,
            color: 'var(--court-gold-dark)',
            marginBottom: '1.25rem',
            letterSpacing: '-0.01em',
            maxWidth: '720px',
            margin: '0 auto 1.25rem auto'
          }}>
            Multi-Agent Constraint-Aware Legal Reasoning & Case Analysis System
          </h2>

          {/* Short, simple description */}
          <p style={{
            fontSize: '16.5px',
            color: 'var(--ink-secondary)',
            lineHeight: 1.65,
            maxWidth: '720px',
            margin: '0 auto 2.25rem auto'
          }}>
            JurisAI analyzes legal cases using specialized AI agents, Indian statutes, 
            Supreme Court precedents, evidence, constraints, and opposing arguments 
            to generate a structured and understandable legal assessment.
          </p>

          {/* Main CTA */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <button 
              onClick={onScrollToInput}
              className="btn-legal-primary"
              style={{ fontSize: '15px', padding: '0.85rem 2.2rem' }}
            >
              Analyze Your Case <ArrowDown size={16} />
            </button>
            <a 
              href="#problem-section"
              className="btn-legal-secondary"
              style={{ fontSize: '15px', padding: '0.85rem 1.75rem', textDecoration: 'none' }}
            >
              Learn More
            </a>
          </div>

          {/* Replaced the ugly 12 laws 91 cases box with a sleek, dignified trust indicator */}
          <div style={{
            marginTop: '2.5rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '1.5rem',
            flexWrap: 'wrap',
            justifyContent: 'center',
            fontSize: '13px',
            color: 'var(--ink-muted)',
            padding: '8px 18px',
            background: '#ffffff',
            border: '1px solid var(--court-parchment-border)',
            borderRadius: '6px'
          }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ color: 'var(--court-gold-dark)', fontWeight: 700 }}>•</span>
              Central Indian Acts
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ color: 'var(--court-gold-dark)', fontWeight: 700 }}>•</span>
              Supreme Court Precedents
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ color: 'var(--court-gold-dark)', fontWeight: 700 }}>•</span>
              Constraint-Aware Verification
            </span>
          </div>
        </div>
      </section>

      {/* 2. What Problem JurisAI Solves (3 clear cards) */}
      <section id="problem-section" style={{
        padding: '4.5rem 1.5rem',
        maxWidth: '1080px',
        margin: '0 auto'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <span className="badge-pill badge-navy" style={{ marginBottom: '0.5rem' }}>
            THE CHALLENGE
          </span>
          <h2 style={{ fontSize: '2.2rem', marginTop: '0.3rem', marginBottom: '0.6rem' }}>
            What Problem JurisAI Solves
          </h2>
          <p style={{ maxWidth: '640px', margin: '0 auto', fontSize: '15.5px' }}>
            Legal disputes under Indian family law involve intricate procedural hurdles and evidentiary standards that can overwhelm anyone without legal training.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.75rem'
        }}>
          {/* Card 1 */}
          <div className="legal-card" style={{ borderTop: '3px solid var(--court-gold)' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '5px', background: '#fdf6e8', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', color: 'var(--court-gold-dark)' }}>
              <ShieldAlert size={20} />
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Hidden Procedural Traps</h3>
            <p style={{ fontSize: '14.5px' }}>
              Statutes contain mandatory cooling-off periods, statutory bars (such as the one-year bar under Section 14), and strict timelines. Litigants often file petitions that get dismissed or delayed due to overlooked procedural rules.
            </p>
          </div>

          {/* Card 2 */}
          <div className="legal-card" style={{ borderTop: '3px solid var(--court-navy)' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '5px', background: '#edf2f7', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', color: 'var(--court-navy)' }}>
              <FileCheck size={20} />
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Misaligned Proof & Evidence</h3>
            <p style={{ fontSize: '14.5px' }}>
              Parties know what happened in their personal lives, but often do not know which documents or records meet judicial standards under Supreme Court rulings. Critical affidavits and proof elements frequently go unsubmitted.
            </p>
          </div>

          {/* Card 3 */}
          <div className="legal-card" style={{ borderTop: '3px solid var(--status-alert)' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '5px', background: '#fdf2f2', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', color: 'var(--status-alert)' }}>
              <Swords size={20} />
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Blindside from the Opposing Party</h3>
            <p style={{ fontSize: '14.5px' }}>
              Most people only consider their own narrative. They enter proceedings unprepared for how opposing counsel will challenge their claims, plead preliminary objections, or dispute income and custody disclosures.
            </p>
          </div>
        </div>
      </section>

      {/* 3. How JurisAI Combines 5 Legal Dimensions */}
      <section id="five-pillars" style={{
        background: '#ffffff',
        borderTop: '1px solid var(--court-parchment-border)',
        borderBottom: '1px solid var(--court-parchment-border)',
        padding: '4.5rem 1.5rem'
      }}>
        <div style={{ maxWidth: '1080px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <span className="badge-pill badge-gold" style={{ marginBottom: '0.5rem' }}>
              REASONING FRAMEWORK
            </span>
            <h2 style={{ fontSize: '2.2rem', marginTop: '0.3rem', marginBottom: '0.6rem' }}>
              How JurisAI Combines 5 Legal Dimensions
            </h2>
            <p style={{ maxWidth: '680px', margin: '0 auto', fontSize: '15.5px' }}>
              A reliable legal evaluation must examine the matter across five interconnected dimensions rather than relying on simple keyword matching.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
            gap: '1.25rem'
          }}>
            <div className="legal-card" style={{ textAlign: 'center', padding: '1.5rem 1.25rem' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: '#eef2f7', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.85rem auto', color: 'var(--court-navy)' }}>
                <BookOpen size={20} />
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.4rem' }}>1. Indian Laws</h4>
              <p style={{ fontSize: '13px', color: 'var(--ink-secondary)' }}>
                Identifies applicable Central Acts, relevant sections, conditions, and statutory provisos.
              </p>
            </div>

            <div className="legal-card" style={{ textAlign: 'center', padding: '1.5rem 1.25rem' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: '#fcf7ed', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.85rem auto', color: 'var(--court-gold-dark)' }}>
                <Gavel size={20} />
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.4rem' }}>2. Supreme Court Precedents</h4>
              <p style={{ fontSize: '13px', color: 'var(--ink-secondary)' }}>
                Extracts binding rulings, judicial interpretations, and official citations.
              </p>
            </div>

            <div className="legal-card" style={{ textAlign: 'center', padding: '1.5rem 1.25rem' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: '#edf7f2', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.85rem auto', color: 'var(--status-pass)' }}>
                <FileCheck size={20} />
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.4rem' }}>3. Evidence Matrix</h4>
              <p style={{ fontSize: '13px', color: 'var(--ink-secondary)' }}>
                Audits facts for proof strength, documentation gaps, and corroboration needs.
              </p>
            </div>

            <div className="legal-card" style={{ textAlign: 'center', padding: '1.5rem 1.25rem' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: '#fffbf2', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.85rem auto', color: 'var(--status-warn)' }}>
                <Lock size={20} />
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.4rem' }}>4. Constraints</h4>
              <p style={{ fontSize: '13px', color: 'var(--ink-secondary)' }}>
                Identifies cooling-off periods, procedural bars, and withdrawal limitations.
              </p>
            </div>

            <div className="legal-card" style={{ textAlign: 'center', padding: '1.5rem 1.25rem' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: '#fdf2f2', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.85rem auto', color: 'var(--status-alert)' }}>
                <Swords size={20} />
              </div>
              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.4rem' }}>5. Opposition</h4>
              <p style={{ fontSize: '13px', color: 'var(--ink-secondary)' }}>
                Anticipates hostile objections, counterarguments, and defense strategies.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. What the Final Analysis Provides (3 clear cards matching Problem section) */}
      <section id="what-it-provides" style={{
        padding: '4.5rem 1.5rem',
        maxWidth: '1080px',
        margin: '0 auto'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <span className="badge-pill badge-navy" style={{ marginBottom: '0.5rem' }}>
            DELIVERABLES
          </span>
          <h2 style={{ fontSize: '2.2rem', marginTop: '0.3rem', marginBottom: '0.6rem' }}>
            What the Final Analysis Provides
          </h2>
          <p style={{ maxWidth: '640px', margin: '0 auto', fontSize: '15.5px' }}>
            The resulting analysis gives you a complete, readable assessment of your position with verified legal authority.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.75rem'
        }}>
          {/* Card 1 */}
          <div className="legal-card" style={{ borderTop: '3px solid var(--court-gold)' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '5px', background: '#fdf6e8', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', color: 'var(--court-gold-dark)' }}>
              <HelpCircle size={20} />
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
              1. Clear "What It Means" Explanations
            </h3>
            <p style={{ fontSize: '14.5px' }}>
              Complex statutes and court precedents are translated into straightforward, everyday language so you can understand your legal rights, options, and limitations without needing to decode technical jargon.
            </p>
          </div>

          {/* Card 2 */}
          <div className="legal-card" style={{ borderTop: '3px solid var(--court-navy)' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '5px', background: '#edf2f7', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', color: 'var(--court-navy)' }}>
              <FileText size={20} />
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
              2. Source Traceability & Citations
            </h3>
            <p style={{ fontSize: '14.5px' }}>
              Every legal point references its exact source, including applicable Central Acts, section numbers, and Supreme Court precedent citations (SCR and INSC numbers) for complete legal verification.
            </p>
          </div>

          {/* Card 3 */}
          <div className="legal-card" style={{ borderTop: '3px solid var(--status-pass)' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '5px', background: '#edf7f2', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', color: 'var(--status-pass)' }}>
              <Download size={20} />
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
              3. Formal Downloadable Legal Brief
            </h3>
            <p style={{ fontSize: '14.5px' }}>
              Export the full, structured assessment as a professionally organized PDF report containing facts, issues, statutory grounds, precedents, evidence evaluation, constraints, and probable outcome.
            </p>
          </div>
        </div>
      </section>

      {/* 5. Observability & System Transparency Section (Phase 17) */}
      <section style={{
        padding: '4.5rem 1.5rem',
        backgroundColor: '#FFFFFF',
        borderTop: '1px solid var(--court-parchment-border)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <span className="badge-pill badge-gold" style={{ marginBottom: '0.5rem' }}>
            PHASE 17 OBSERVABILITY
          </span>
          <h2 style={{ fontSize: '2.2rem', marginTop: '0.3rem', marginBottom: '0.6rem', color: 'var(--court-navy)', fontWeight: 700 }}>
            Transparent AI Reasoning Pipeline
          </h2>
          <p style={{ maxWidth: '720px', margin: '0 auto', fontSize: '15.5px', color: 'var(--ink-secondary)', lineHeight: '1.6' }}>
            JurisAI tracks each case analysis using a unique analysis ID, records agent execution, monitors retrieval performance, and audits the final reasoning for errors and inconsistencies.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.75rem',
          maxWidth: '1080px',
          margin: '0 auto'
        }}>
          {/* Card 1: Agent Monitoring */}
          <div className="legal-card" style={{ borderTop: '3px solid var(--court-navy)' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '6px', background: 'var(--court-parchment-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', color: 'var(--court-navy)' }}>
              <Cpu size={22} />
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', fontWeight: 700 }}>
              Agent Monitoring
            </h3>
            <p style={{ fontSize: '14.5px', color: 'var(--ink-secondary)', lineHeight: '1.5' }}>
              Track execution and performance of all 8 legal reasoning agents. Monitor start and finish timestamps, durations, and state transitions with zero blind spots.
            </p>
          </div>

          {/* Card 2: RAG Monitoring */}
          <div className="legal-card" style={{ borderTop: '3px solid var(--court-gold)' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '6px', background: '#fdf6e8', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', color: 'var(--court-gold-dark)' }}>
              <Activity size={22} />
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', fontWeight: 700 }}>
              RAG Monitoring
            </h3>
            <p style={{ fontSize: '14.5px', color: 'var(--ink-secondary)', lineHeight: '1.5' }}>
              Measure retrieved legal sources, document counts, and retrieval latency across the 916-chunk statutory index and Supreme Court precedent vector store.
            </p>
          </div>

          {/* Card 3: Audit & Self-Correction */}
          <div className="legal-card" style={{ borderTop: '3px solid var(--status-pass)' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '6px', background: '#edf7f2', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem', color: 'var(--status-pass)' }}>
              <ShieldAlert size={22} />
            </div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', fontWeight: 700 }}>
              Audit & Self-Correction
            </h3>
            <p style={{ fontSize: '14.5px', color: 'var(--ink-secondary)', lineHeight: '1.5' }}>
              Track audit results and re-analysis iterations when errors are detected. Verify citation authenticity against ChromaDB before generating judicial decrees.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
