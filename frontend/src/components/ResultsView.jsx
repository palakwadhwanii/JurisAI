import React, { useState } from 'react';

export default function ResultsView({ analysisData }) {
  const [copied, setCopied] = useState(false);

  if (!analysisData || !analysisData.final_judgment) {
    return null;
  }

  const { final_judgment, outcome } = analysisData;

  const handleCopy = () => {
    navigator.clipboard.writeText(final_judgment);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([final_judgment], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `JurisAI_Case_Analysis_${Date.now()}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <section id="results-view" style={{ marginBottom: '3rem' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '0.8rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <span className="notebook-tag tag-ink" style={{ marginRight: '0.5rem' }}>Component 4</span>
          <span className="mono" style={{ fontSize: '13px', color: 'var(--text-muted)' }}>results-view.tsx</span>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={handleCopy} className="btn-secondary" style={{ fontSize: '12px' }}>
            {copied ? '✓ Copied to Clipboard' : 'Copy Opinion Text'}
          </button>
          <button onClick={handleDownload} className="btn-secondary" style={{ fontSize: '12px' }}>
            Download Markdown Brief (.md)
          </button>
        </div>
      </div>

      <div style={{
        background: '#fff',
        border: '1px solid var(--border-dark)',
        padding: '2.5rem 2rem',
        boxShadow: '0 2px 10px rgba(0,0,0,0.03)'
      }}>
        <div style={{
          borderBottom: '2px solid var(--border-dark)',
          paddingBottom: '1rem',
          marginBottom: '2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <div className="mono" style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Supreme Court & Family Court Jurisprudence Assessment
            </div>
            <h2 style={{ fontSize: '1.9rem', marginTop: '0.3rem', fontWeight: 600 }}>
              Judicial Opinion & Case Synthesis
            </h2>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span className={`notebook-tag ${outcome === 'PASS' ? 'tag-sage' : outcome === 'RECOVERED' ? 'tag-amber' : 'tag-terra'}`} style={{ fontSize: '12px' }}>
              Final Audit: {outcome}
            </span>
            <div style={{ fontSize: '11px', color: 'var(--text-faint)', marginTop: '4px' }}>
              Synthesized by Judge Agent
            </div>
          </div>
        </div>

        {/* Formatted Markdown Content */}
        <div className="opinion-content" style={{
          fontSize: '14.5px',
          lineHeight: '1.75',
          color: '#24221f'
        }}>
          {final_judgment.split('\n\n').map((paragraph, pIdx) => {
            const p = paragraph.trim();
            if (p.startsWith('# ')) {
              return null; // Skip main title as rendered in header
            }
            if (p.startsWith('### ')) {
              return (
                <h3 key={pIdx} style={{
                  fontSize: '1.25rem',
                  marginTop: '1.8rem',
                  marginBottom: '0.6rem',
                  borderBottom: '1px solid var(--border-line)',
                  paddingBottom: '4px',
                  color: 'var(--text-main)'
                }}>
                  {p.replace('### ', '')}
                </h3>
              );
            }
            if (p.startsWith('> [!')) {
              return (
                <div key={pIdx} style={{
                  background: 'var(--accent-amber-bg)',
                  borderLeft: '4px solid var(--accent-amber)',
                  padding: '10px 14px',
                  marginBottom: '1rem',
                  fontSize: '13px'
                }}>
                  {p.replace(/>\s*\[!\w+\]\s*/g, '')}
                </div>
              );
            }
            if (p.startsWith('|')) {
              // Table rendering
              const rows = p.split('\n').filter(r => r.trim().startsWith('|'));
              return (
                <div key={pIdx} style={{ overflowX: 'auto', margin: '1rem 0' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12.5px', background: '#fff' }}>
                    <tbody>
                      {rows.map((row, rIdx) => {
                        const cells = row.split('|').filter((_, cIdx, arr) => cIdx > 0 && cIdx < arr.length - 1);
                        if (rIdx === 1) return null; // Separator row
                        const isHeader = rIdx === 0;
                        return (
                          <tr key={rIdx} style={{ background: isHeader ? 'var(--bg-subtle)' : 'transparent', borderBottom: '1px solid var(--border-line)' }}>
                            {cells.map((cell, cIdx) => (
                              isHeader ? (
                                <th key={cIdx} style={{ padding: '8px 10px', textAlign: 'left', fontWeight: 600, border: '1px solid var(--border-line)' }}>
                                  {cell.trim()}
                                </th>
                              ) : (
                                <td key={cIdx} style={{ padding: '7px 10px', border: '1px solid var(--border-line)' }}>
                                  {cell.trim()}
                                </td>
                              )
                            ))}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              );
            }
            if (p.startsWith('- ')) {
              const items = p.split('\n').filter(i => i.trim().startsWith('- '));
              return (
                <ul key={pIdx} style={{ paddingLeft: '1.4rem', marginBottom: '1rem' }}>
                  {items.map((item, iIdx) => (
                    <li key={iIdx} style={{ marginBottom: '4px' }}>
                      {item.replace(/^- /, '')}
                    </li>
                  ))}
                </ul>
              );
            }
            return (
              <p key={pIdx} style={{ marginBottom: '1rem' }}>
                {p}
              </p>
            );
          })}
        </div>
      </div>
    </section>
  );
}
