import React, { useState } from 'react';

export default function AnalysisDashboard({ analysisData, loading }) {
  const [activeTab, setActiveTab] = useState('pipeline');

  if (loading) {
    return (
      <div style={{
        border: '1px solid var(--border-dark)',
        padding: '2rem',
        background: '#fff',
        marginBottom: '2rem',
        textAlign: 'center'
      }}>
        <div className="mono" style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
          MULTI-AGENT ORCHESTRATION IN PROGRESS
        </div>
        <h3 style={{ fontSize: '1.4rem', marginBottom: '0.8rem' }}>
          Fan-out: Querying Law, Precedent and Evidence Agents...
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '14px', maxWidth: '520px', margin: '0 auto 1.5rem auto' }}>
          Searching 916 chunks in ChromaDB. Constraint Hunter is identifying statutory cooling-off periods and bars. Auditor is validating citations against India Code.
        </p>
        <div style={{ display: 'inline-flex', gap: '0.5rem', alignItems: 'center' }}>
          <span className="notebook-tag tag-terra">Law Agent</span>
          <span className="mono">→</span>
          <span className="notebook-tag tag-ink">Precedent Agent</span>
          <span className="mono">→</span>
          <span className="notebook-tag tag-amber">Constraint Hunter</span>
          <span className="mono">→</span>
          <span className="notebook-tag tag-sage">Auditor Loop</span>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div style={{
        border: '1px solid var(--border-line)',
        padding: '2rem',
        background: 'var(--bg-subtle)',
        marginBottom: '2rem',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '12px', fontFamily: 'var(--mono-font)', color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
          Component 3: analysis-dashboard.tsx
        </div>
        <h3 style={{ fontSize: '1.3rem', color: 'var(--text-muted)', fontWeight: 500, marginBottom: '0.4rem' }}>
          Agent Execution Telemetry Ready
        </h3>
        <p style={{ fontSize: '13.5px', color: 'var(--text-faint)', maxWidth: '480px', margin: '0 auto' }}>
          Enter a case narrative above and click execute to trigger the 8-agent reasoning loop. 
          Auditor state, iteration steps, and inter-agent dependencies will stream here.
        </p>
      </div>
    );
  }

  const { outcome, total_iterations, audit_history, elapsed_seconds, case_state, agent_outputs } = analysisData;
  const latestAudit = audit_history && audit_history.length > 0 ? audit_history[audit_history.length - 1] : null;

  return (
    <section id="analysis-dashboard" style={{ marginBottom: '2.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '0.8rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <span className="notebook-tag tag-sage" style={{ marginRight: '0.5rem' }}>Component 3</span>
          <span className="mono" style={{ fontSize: '13px', color: 'var(--text-muted)' }}>analysis-dashboard.tsx</span>
        </div>
        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
          <span className="mono" style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Total Runtime: <strong>{elapsed_seconds}s</strong>
          </span>
          <span className="mono" style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Iterations: <strong>{total_iterations} / 3</strong>
          </span>
        </div>
      </div>

      {/* Outcome Banner */}
      <div style={{
        border: '1px solid var(--border-dark)',
        background: outcome === 'PASS' ? '#f4faf8' : outcome === 'RECOVERED' ? '#fffaf0' : '#fdf2f2',
        borderLeftWidth: '6px',
        borderLeftColor: outcome === 'PASS' ? 'var(--accent-sage)' : outcome === 'RECOVERED' ? 'var(--accent-amber)' : 'var(--accent-terra)',
        padding: '1.2rem',
        marginBottom: '1.2rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.8rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '4px' }}>
              <span className={`notebook-tag ${outcome === 'PASS' ? 'tag-sage' : outcome === 'RECOVERED' ? 'tag-amber' : 'tag-terra'}`} style={{ fontWeight: 600 }}>
                STATUS: {outcome}
              </span>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'var(--mono-font)' }}>
                {outcome === 'PASS' && 'Audited clean on first iteration.'}
                {outcome === 'RECOVERED' && 'Auditor flagged error on Iteration 1. ReanalysisRouter successfully self-corrected.'}
                {outcome === 'HUMAN_REVIEW_REQUIRED' && 'Unresolved error after 3 iterations. Withheld auto-decree for safety.'}
              </span>
            </div>
            <div style={{ fontSize: '14px', color: 'var(--text-main)', marginTop: '4px' }}>
              <strong>Claims Handled:</strong> {case_state.claims && case_state.claims.join(', ')}
            </div>
          </div>
          <div style={{ fontSize: '12px', fontFamily: 'var(--mono-font)', color: 'var(--text-muted)', textAlign: 'right' }}>
            Auditor Errors: {latestAudit ? latestAudit.errors.length : 0} | Citations Checked: {latestAudit ? latestAudit.citation_verifications.length : 0}
          </div>
        </div>
      </div>

      {/* Tab Switcher */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-dark)', marginBottom: '1rem', gap: '0.5rem' }}>
        <button
          onClick={() => setActiveTab('pipeline')}
          style={{
            background: activeTab === 'pipeline' ? 'var(--text-main)' : 'transparent',
            color: activeTab === 'pipeline' ? '#fff' : 'var(--text-main)',
            border: 'none',
            padding: '7px 14px',
            fontSize: '13px',
            cursor: 'pointer',
            fontFamily: 'var(--sans-font)',
            fontWeight: 500
          }}
        >
          Workflow Topology & Audit Trace
        </button>
        <button
          onClick={() => setActiveTab('agents')}
          style={{
            background: activeTab === 'agents' ? 'var(--text-main)' : 'transparent',
            color: activeTab === 'agents' ? '#fff' : 'var(--text-main)',
            border: 'none',
            padding: '7px 14px',
            fontSize: '13px',
            cursor: 'pointer',
            fontFamily: 'var(--sans-font)',
            fontWeight: 500
          }}
        >
          Agent Raw Telemetry
        </button>
      </div>

      {activeTab === 'pipeline' && (
        <div style={{ background: '#fff', border: '1px solid var(--border-line)', padding: '1.2rem' }}>
          <div style={{ fontSize: '12px', textTransform: 'uppercase', fontFamily: 'var(--mono-font)', color: 'var(--text-faint)', marginBottom: '0.8rem' }}>
            Multi-Agent Execution Directed Graph:
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
            {/* Step 1: Case Manager */}
            <div style={{ padding: '8px 12px', background: 'var(--bg-subtle)', borderLeft: '3px solid var(--text-main)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span className="mono" style={{ fontWeight: 600 }}>1. Case Manager Agent</span>
                <span className="notebook-tag">Normalized Input</span>
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Extracted {case_state.facts ? case_state.facts.length : 0} factual propositions, {case_state.claims ? case_state.claims.length : 0} legal claims.
              </div>
            </div>

            {/* Step 2: Fan out */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.8rem', paddingLeft: '1rem', borderLeft: '2px solid var(--border-line)' }}>
              <div style={{ padding: '8px 10px', background: '#fff', border: '1px solid var(--border-line)' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-terra)' }}>2a. Law Agent</div>
                <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                  Identified {agent_outputs.law_sections ? agent_outputs.law_sections.length : 0} statutory sections in ChromaDB.
                </div>
              </div>
              <div style={{ padding: '8px 10px', background: '#fff', border: '1px solid var(--border-line)' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-ink)' }}>2b. Precedent Agent</div>
                <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                  Retrieved {agent_outputs.precedents ? agent_outputs.precedents.length : 0} Supreme Court precedents (2023 to 2025).
                </div>
              </div>
              <div style={{ padding: '8px 10px', background: '#fff', border: '1px solid var(--border-line)' }}>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-sage)' }}>2c. Evidence Agent</div>
                <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                  Evaluated {agent_outputs.evidence_support ? agent_outputs.evidence_support.length : 0} supporting facts, {agent_outputs.evidence_gaps ? agent_outputs.evidence_gaps.length : 0} gaps.
                </div>
              </div>
            </div>

            {/* Step 3: Constraint Hunter */}
            <div style={{ padding: '8px 12px', background: 'var(--bg-subtle)', borderLeft: '3px solid var(--accent-amber)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span className="mono" style={{ fontWeight: 600 }}>3. Constraint Hunter Agent</span>
                <span className="notebook-tag tag-amber">Barrier Analysis</span>
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Flagged {agent_outputs.procedural_constraints ? agent_outputs.procedural_constraints.length : 0} procedural bars and {agent_outputs.substantive_constraints ? agent_outputs.substantive_constraints.length : 0} statutory conditions.
              </div>
            </div>

            {/* Step 4: Opposition */}
            <div style={{ padding: '8px 12px', background: 'var(--bg-subtle)', borderLeft: '3px solid var(--accent-terra)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span className="mono" style={{ fontWeight: 600 }}>4. Opposition Agent</span>
                <span className="notebook-tag tag-terra">Adversarial Defense</span>
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Framed {agent_outputs.opposition_objections ? agent_outputs.opposition_objections.length : 0} objections and {agent_outputs.opposition_counterarguments ? agent_outputs.opposition_counterarguments.length : 0} counterarguments.
              </div>
            </div>

            {/* Step 5: Auditor */}
            <div style={{ padding: '8px 12px', background: 'var(--bg-subtle)', borderLeft: '3px solid var(--accent-sage)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span className="mono" style={{ fontWeight: 600 }}>5. Auditor Agent & Reanalysis Router</span>
                <span className="notebook-tag tag-sage">Quality Gate</span>
              </div>
              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Audit history across {audit_history.length} iteration(s). Status: <strong>{latestAudit ? latestAudit.audit_status : 'N/A'}</strong>.
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'agents' && (
        <div style={{ background: '#fff', border: '1px solid var(--border-line)', padding: '1.2rem' }}>
          <div style={{ fontSize: '13px', marginBottom: '1rem' }}>
            <strong>Raw Telemetry from Constraint Hunter:</strong>
            <ul style={{ paddingLeft: '1.2rem', marginTop: '4px', fontSize: '12.5px', color: 'var(--text-muted)' }}>
              {agent_outputs.procedural_constraints && agent_outputs.procedural_constraints.map((c, i) => (
                <li key={i}>{c.constraint || JSON.stringify(c)}</li>
              ))}
            </ul>
          </div>
          <div style={{ fontSize: '13px', marginBottom: '1rem' }}>
            <strong>Raw Telemetry from Opposition Agent:</strong>
            <ul style={{ paddingLeft: '1.2rem', marginTop: '4px', fontSize: '12.5px', color: 'var(--text-muted)' }}>
              {agent_outputs.opposition_objections && agent_outputs.opposition_objections.map((o, i) => (
                <li key={i}>{o}</li>
              ))}
            </ul>
          </div>
          <div style={{ fontSize: '13px' }}>
            <strong>Audit Citations Verification:</strong>
            <div style={{ maxHeight: '180px', overflowY: 'auto', border: '1px solid var(--border-line)', marginTop: '6px', padding: '6px' }}>
              {latestAudit && latestAudit.citation_verifications.map((v, i) => (
                <div key={i} style={{ fontSize: '11.5px', display: 'flex', justifyContent: 'space-between', padding: '3px 0', borderBottom: '1px solid var(--bg-subtle)' }}>
                  <span>{v.entity || `${v.act} Sec ${v.section}`}</span>
                  <span className="mono" style={{ color: v.valid ? 'var(--accent-sage)' : 'var(--accent-terra)' }}>
                    {v.status || (v.valid ? 'VALID' : 'INVALID')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
