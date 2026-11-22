import React from 'react';

export default function ProjectStory() {
  return (
    <header style={{ marginBottom: '3rem' }}>
      {/* Student Project Meta Banner */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'baseline',
        borderBottom: '2px solid var(--border-dark)',
        paddingBottom: '0.6rem',
        marginBottom: '2rem',
        flexWrap: 'wrap',
        gap: '0.5rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <span className="mono" style={{ fontSize: '13px', fontWeight: 600, background: 'var(--text-main)', color: '#fff', padding: '2px 6px' }}>
            PROJECT NOTEBOOK #16
          </span>
          <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Indian Family Law Reasoning System
          </span>
        </div>
        <div className="mono" style={{ fontSize: '12px', color: 'var(--text-faint)' }}>
          Student Capstone Research : Term Project 2026
        </div>
      </div>

      {/* Editorial Headline & Story */}
      <div style={{ maxWidth: '820px', marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.6rem', lineHeight: '1.2', fontWeight: 700, marginBottom: '1.2rem', letterSpacing: '-0.02em' }}>
          Constraint-Aware Legal Reasoning Across 12 Indian Family Law Acts
        </h1>
        <p style={{ fontSize: '16.5px', lineHeight: '1.65', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          Standard language models fail predictably when applied to Indian matrimonial law. 
          When we tested raw models on mutual consent divorce, they hallucinated non-existent sections such as "Section 33(2)" 
          and ignored mandatory statutory cooling-off periods under Section 13B(2) of the Hindu Marriage Act.
        </p>
        <p style={{ fontSize: '15px', lineHeight: '1.65', color: 'var(--text-muted)' }}>
          To solve this, we collected 12 central statutes directly from India Code, enriched 91 candidate Supreme Court judgments 
          from 2023 to 2025, and architected an 8-agent pipeline. The system hunts statutory provisos, evaluates adversarial counterarguments, 
          and audits its own citations before synthesizing a decree.
        </p>
      </div>

      {/* Asymmetric Engineering Log & Database Metrics */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1.4fr 1fr',
        gap: '2rem',
        background: 'var(--bg-subtle)',
        padding: '1.5rem',
        border: '1px solid var(--border-line)',
        marginBottom: '2rem'
      }}>
        <div>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', fontFamily: 'var(--mono-font)', color: 'var(--text-faint)', marginBottom: '0.4rem' }}>
            Core Engineering Premise (From our lab notes)
          </div>
          <div style={{ fontSize: '13.5px', color: 'var(--text-main)', lineHeight: '1.6' }}>
            "A legal answer without constraint analysis is malpractice. If a couple files for mutual consent divorce, 
            the court cannot simply decree dissolution without verifying the 1-year living apart threshold under Section 13B(1), 
            the 6-month statutory waiting interval under 13B(2), and compliance with Supreme Court guidelines in Amardeep Singh v. Harveen Kaur."
          </div>
        </div>

        <div style={{ borderLeft: '1px solid var(--border-line)', paddingLeft: '1.5rem' }}>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', fontFamily: 'var(--mono-font)', color: 'var(--text-faint)', marginBottom: '0.4rem' }}>
            Verified Corpus Ground Truth
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem', fontSize: '12.5px' }}>
            <div>
              <span className="mono" style={{ fontWeight: 600, fontSize: '16px', display: 'block' }}>12</span>
              <span style={{ color: 'var(--text-muted)' }}>Central Acts Indexed</span>
            </div>
            <div>
              <span className="mono" style={{ fontWeight: 600, fontSize: '16px', display: 'block' }}>91</span>
              <span style={{ color: 'var(--text-muted)' }}>SC Cases (2023-2025)</span>
            </div>
            <div>
              <span className="mono" style={{ fontWeight: 600, fontSize: '16px', display: 'block' }}>916</span>
              <span style={{ color: 'var(--text-muted)' }}>ChromaDB Chunks</span>
            </div>
            <div>
              <span className="mono" style={{ fontWeight: 600, fontSize: '16px', display: 'block' }}>8</span>
              <span style={{ color: 'var(--text-muted)' }}>Specialized Agents</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
