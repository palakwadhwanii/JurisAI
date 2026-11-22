import React from 'react';

export default function CaseInput({
  caseText,
  setCaseText,
  onAnalyze,
  loading,
  sampleCases,
  onSelectSample,
  selectedSampleId,
  testFault,
  setTestFault
}) {
  return (
    <section id="case-input" style={{ marginBottom: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '0.8rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <span className="notebook-tag tag-terra" style={{ marginRight: '0.5rem' }}>Component 1</span>
          <span className="mono" style={{ fontSize: '13px', color: 'var(--text-muted)' }}>case-input.tsx</span>
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-faint)', fontStyle: 'italic' }}>
          Supports 12 Indian Family Law Acts (Central Statutes)
        </div>
      </div>

      <h2 style={{ fontSize: '1.7rem', marginBottom: '0.5rem', fontWeight: 600 }}>
        Matrimonial Dispute Intake
      </h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '1.2rem', maxWidth: '680px' }}>
        Paste the factual narrative of the dispute. You can state facts conversationally, 
        such as years of marriage, duration of separation, pending police complaints, or drafted settlement terms. 
        The Case Manager Agent will extract normalized factual entities.
      </p>

      {/* Benchmark Case Selectors */}
      <div style={{ marginBottom: '1rem' }}>
        <div style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-faint)', marginBottom: '0.4rem', fontFamily: 'var(--mono-font)' }}>
          Student Benchmark Case Library:
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {sampleCases.map((sc) => (
            <button
              key={sc.id}
              onClick={() => onSelectSample(sc)}
              className="btn-secondary"
              style={{
                fontSize: '12px',
                backgroundColor: selectedSampleId === sc.id ? 'var(--bg-warm)' : 'transparent',
                borderColor: selectedSampleId === sc.id ? 'var(--text-main)' : 'var(--border-line)',
                fontWeight: selectedSampleId === sc.id ? 600 : 400
              }}
            >
              {sc.title}
            </button>
          ))}
        </div>
      </div>

      {/* Main Textarea */}
      <div style={{ position: 'relative', border: '1px solid var(--border-dark)', background: '#fff' }}>
        <textarea
          value={caseText}
          onChange={(e) => setCaseText(e.target.value)}
          rows={6}
          placeholder="e.g. Parties married in 2020 under Hindu Marriage Act, living separately for over 2 years. Settlement reached. Seeking mutual consent divorce under Section 13B with waiver of 6-month cooling off period..."
          style={{
            width: '100%',
            padding: '1rem',
            border: 'none',
            outline: 'none',
            fontSize: '14.5px',
            lineHeight: '1.6',
            fontFamily: 'var(--sans-font)',
            resize: 'vertical',
            color: 'var(--text-main)'
          }}
        />
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0.5rem 0.8rem',
          borderTop: '1px solid var(--border-line)',
          background: 'var(--bg-subtle)',
          fontSize: '12px',
          color: 'var(--text-muted)'
        }}>
          <div>
            Characters: <span className="mono">{caseText.length}</span> | Words: <span className="mono">{caseText.trim() ? caseText.trim().split(/\s+/).length : 0}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '11px', textTransform: 'uppercase', fontFamily: 'var(--mono-font)', color: 'var(--text-faint)' }}>Self-Check Mode:</span>
            <select
              value={testFault || ''}
              onChange={(e) => setTestFault(e.target.value || null)}
              style={{
                fontSize: '11px',
                fontFamily: 'var(--mono-font)',
                padding: '2px 4px',
                background: '#fff',
                border: '1px solid var(--border-line)'
              }}
            >
              <option value="">Standard (Auto-Audit)</option>
              <option value="CITATION_ERROR">Inject Section Error (Test Self-Correction)</option>
              <option value="PERSISTENT_UNRESOLVED">Inject Irreconcilable Error (Test Human Review)</option>
            </select>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-start', marginTop: '1rem', alignItems: 'center', gap: '1rem' }}>
        <button
          onClick={onAnalyze}
          disabled={loading || !caseText.trim()}
          className="btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          {loading ? (
            <>
              <span className="mono" style={{ animation: 'spin 1s linear infinite' }}>⚙️</span>
              <span>Running 8-Agent Pipeline...</span>
            </>
          ) : (
            <>
              <span>Execute Multi-Agent Case Analysis</span>
              <span className="mono" style={{ fontSize: '12px' }}>→</span>
            </>
          )}
        </button>
        <span style={{ fontSize: '12px', color: 'var(--text-faint)', fontStyle: 'italic' }}>
          Routes through ChromaDB (916 chunks) and Phase 15 self-checking router.
        </span>
      </div>
    </section>
  );
}
