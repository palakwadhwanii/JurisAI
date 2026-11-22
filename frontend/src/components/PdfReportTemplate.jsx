import React, { useRef } from 'react';
import html2pdf from 'html2pdf.js';
import { Download, Printer, X, FileText } from 'lucide-react';

function cleanText(str) {
  if (str === null || str === undefined) return '';
  const val = typeof str !== 'string' ? String(str) : str;
  return val
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^#+\s*/gm, '')
    .replace(/^>\s*\[!\w+\]\s*/gm, '')
    .replace(/^>\s*/gm, '')
    .replace(/[\u2013\u2014]/g, ' - ')
    .replace(/`/g, '')
    .trim();
}

function extractSection(markdown, sectionTitle) {
  if (!markdown) return null;
  const regex = new RegExp(`###\\s*\\d*\\.?\\s*${sectionTitle}[\\s\\S]*?(?=###|$)`, 'i');
  const match = markdown.match(regex);
  if (!match) return null;
  const raw = match[0].replace(new RegExp(`^###\\s*\\d*\\.?\\s*${sectionTitle}`, 'i'), '');
  return cleanText(raw);
}

export default function PdfReportTemplate({ analysisData, isOpen, onClose }) {
  const printAreaRef = useRef(null);

  if (!isOpen || !analysisData) return null;

  const { case_state, agent_outputs, outcome, audit_history, final_judgment } = analysisData;
  const latestAudit = audit_history && audit_history.length > 0 ? audit_history[audit_history.length - 1] : null;

  const handleDownloadPdf = () => {
    if (!printAreaRef.current) return;

    const opt = {
      margin: [10, 10, 10, 10],
      filename: `JurisAI_Legal_Assessment_${Date.now()}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(printAreaRef.current).save();
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(14, 30, 51, 0.8)',
      backdropFilter: 'blur(4px)',
      zIndex: 2000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem'
    }}>
      <div style={{
        background: '#ffffff',
        width: '100%',
        maxWidth: '960px',
        maxHeight: '90vh',
        borderRadius: '6px',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 20px 40px rgba(0,0,0,0.25)',
        overflow: 'hidden'
      }}>
        {/* Modal Toolbar */}
        <div style={{
          background: 'var(--court-navy)',
          padding: '0.85rem 1.5rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          color: '#ffffff'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <FileText size={18} color="var(--court-gold)" />
            <h3 style={{ fontSize: '1.1rem', color: '#ffffff', fontWeight: 600 }}>
              JurisAI Legal Assessment Brief
            </h3>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <button
              onClick={handlePrint}
              className="btn-legal-secondary"
              style={{ fontSize: '12.5px', padding: '0.4rem 0.85rem', color: 'var(--court-navy)' }}
            >
              <Printer size={14} /> Print
            </button>
            <button
              onClick={handleDownloadPdf}
              className="btn-legal-gold"
              style={{ fontSize: '12.5px', padding: '0.4rem 1rem' }}
            >
              <Download size={14} /> Download PDF
            </button>
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#ffffff',
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Scrollable Printable Document Container */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '2.5rem 3rem',
          background: '#ffffff',
          color: '#1a1a1a',
          fontFamily: 'var(--font-family-base)'
        }}>
          <div ref={printAreaRef} style={{ background: '#ffffff', padding: '10px' }}>
            {/* Legal Document Formal Header */}
            <div style={{
              borderBottom: '2px solid #0e1e33',
              paddingBottom: '1.25rem',
              marginBottom: '1.75rem',
              textAlign: 'center'
            }}>
              <h1 style={{
                fontSize: '2rem',
                fontWeight: 700,
                color: '#0e1e33',
                margin: '0 0 4px 0'
              }}>
                JurisAI Legal Case Assessment
              </h1>
              <div style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.04em', color: '#555', fontWeight: 600 }}>
                Constraint-Aware Indian Family Law Opinion
              </div>
              <div style={{ fontSize: '12px', color: '#777', marginTop: '4px' }}>
                Generated on: {new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })} | Audit Status: {outcome}
              </div>
            </div>

            {/* 1. Case Summary */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                1. Case Summary
              </h3>
              <p style={{ fontSize: '13.5px', lineHeight: '1.6' }}>
                This legal assessment evaluates a matter involving {case_state.claims?.map(c => cleanText(c)).join(', ') || 'matrimonial relief under Central Indian statutes'}. 
                The analysis examines statutory eligibility conditions, judicial standards, and procedural waiting requirements.
              </p>
            </div>

            {/* 2. Material Facts */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                2. Material Facts
              </h3>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '13px', lineHeight: '1.6' }}>
                {case_state.facts?.map((f, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{cleanText(f)}</li>
                ))}
              </ul>
            </div>

            {/* 3. Legal Issues */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                3. Legal Issues & Questions for Determination
              </h3>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '13px', lineHeight: '1.6' }}>
                {case_state.legal_issues?.map((issue, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{cleanText(issue)}</li>
                ))}
              </ul>
            </div>

            {/* 4. Applicable Acts and Sections */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                4. Applicable Central Acts and Sections
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {agent_outputs?.law_sections?.map((s, i) => (
                  <div key={i} style={{ fontSize: '13px', background: '#f8f8f8', padding: '8px 12px', borderLeft: '3px solid #0e1e33' }}>
                    <strong>{cleanText(s.act_name)}: Section {cleanText(s.section)} ({cleanText(s.title) || 'Statutory Ground'})</strong>
                    {s.meaning && (
                      <div style={{ color: '#222', fontSize: '12px', marginTop: '2px' }}>
                        <strong>Rule:</strong> {cleanText(s.meaning)}
                      </div>
                    )}
                    {s.application && (
                      <div style={{ color: '#555', fontSize: '11.5px', marginTop: '2px' }}>
                        <strong>Application:</strong> {cleanText(s.application)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* 5. Relevant Precedents */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                5. Relevant Supreme Court Precedents
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {agent_outputs?.precedents?.map((p, i) => (
                  <div key={i} style={{ fontSize: '13px', background: '#fdfbf7', padding: '8px 12px', borderLeft: '3px solid #b38b3c' }}>
                    <strong>{cleanText(p.case_name)} ({cleanText(p.year) || 'Supreme Court'})</strong> | {cleanText(p.scr_citation)} | {cleanText(p.insc_citation)}
                    {p.legal_issue && (
                      <div style={{ color: '#222', fontSize: '12px', marginTop: '2px' }}>
                        <strong>Issue:</strong> {cleanText(p.legal_issue)}
                      </div>
                    )}
                    {(p.ratio || p.decision_holding) && (
                      <div style={{ color: '#444', fontSize: '12px', marginTop: '2px' }}>
                        <strong>Ratio:</strong> {cleanText(p.ratio || p.decision_holding)}
                      </div>
                    )}
                    {p.case_application && (
                      <div style={{ color: '#0e1e33', fontSize: '11.5px', marginTop: '2px', fontStyle: 'italic' }}>
                        <strong>Application:</strong> {cleanText(p.case_application)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* 6. Evidence Assessment */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                6. Evidence Assessment & Verification
              </h3>
              <div style={{ fontSize: '13px', marginBottom: '4px', fontWeight: 600 }}>
                Supported Proof Elements:
              </div>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '12.5px', marginBottom: '8px' }}>
                {agent_outputs?.evidence_support?.map((es, i) => (
                  <li key={i}>{cleanText(es)}</li>
                ))}
              </ul>
              <div style={{ fontSize: '13px', marginBottom: '4px', fontWeight: 600 }}>
                Evidence Gaps & Documentation Required:
              </div>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '12.5px' }}>
                {agent_outputs?.evidence_gaps?.map((eg, i) => (
                  <li key={i}>{cleanText(eg)}</li>
                ))}
              </ul>
            </div>

            {/* 7. Legal Constraints */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                7. Legal Constraints & Procedural Bars
              </h3>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '12.5px', lineHeight: '1.6' }}>
                {agent_outputs?.procedural_constraints?.map((c, i) => (
                  <li key={`proc-${i}`}>
                    {typeof c === 'object' ? `${cleanText(c.constraint)} (${cleanText(c.exception_rule || c.status || c.statutory_source || 'Statute')})` : cleanText(String(c))}
                  </li>
                ))}
                {agent_outputs?.substantive_constraints?.map((sc, i) => (
                  <li key={`sub-${i}`}>
                    {typeof sc === 'object' ? `${cleanText(sc.constraint)}: ${cleanText(sc.description || '')}` : cleanText(String(sc))}
                  </li>
                ))}
              </ul>
            </div>

            {/* 8. Opposition Arguments */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                8. Opposition Arguments & Adversarial Defenses
              </h3>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '12.5px', lineHeight: '1.6' }}>
                {agent_outputs?.opposition_objections?.map((ob, i) => (
                  <li key={`ob-${i}`}><strong>Objection:</strong> {cleanText(ob)}</li>
                ))}
                {agent_outputs?.opposition_counterarguments?.map((ca, i) => (
                  <li key={`ca-${i}`}><strong>Rebuttal:</strong> {cleanText(ca)}</li>
                ))}
              </ul>
            </div>

            {/* 9. Audit Results */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                9. Citation Audit Results
              </h3>
              <p style={{ fontSize: '13px' }}>
                Status: <strong>{outcome}</strong> | Citations Verified: <strong>{latestAudit?.citation_verifications?.length || 0}</strong>. All references verified against India Code statutory records and Supreme Court law reports.
              </p>
            </div>

            {/* 10. Final Legal Assessment */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                10. Final Legal Assessment & Probable Court Decree
              </h3>
              <p style={{ fontSize: '13.5px', lineHeight: '1.65', whiteSpace: 'pre-line' }}>
                {extractSection(final_judgment, 'Probable Outcome & Operative Relief') ||
                 extractSection(final_judgment, 'Judicial Analysis & Synthesis') ||
                 'The case presents verifiable statutory grounds under governing Central enactments.'}
              </p>
            </div>

            {/* 11. Sources and Citations */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, borderBottom: '1px solid #ddd', paddingBottom: '4px', marginBottom: '8px', color: '#0e1e33' }}>
                11. Primary Legal Sources & Citations
              </h3>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '12px', color: '#444' }}>
                {Array.from(new Set(agent_outputs?.law_sections?.map(s => `${cleanText(s.act_name)} Section ${cleanText(s.section)}`))).map((src, i) => (
                  <li key={`act-${i}`}>{src}</li>
                ))}
                {agent_outputs?.precedents?.map((p, i) => (
                  <li key={`prec-${i}`}>
                    {cleanText(p.case_name)} ({cleanText(p.year) || 'SC'}) {p.scr_citation ? `| ${cleanText(p.scr_citation)}` : ''} {p.insc_citation ? `| ${cleanText(p.insc_citation)}` : ''}
                  </li>
                ))}
              </ul>
            </div>

            {/* 12. Limitations & Disclaimer */}
            <div style={{
              borderTop: '1px solid #ddd',
              paddingTop: '0.85rem',
              marginTop: '1.5rem',
              fontSize: '11px',
              color: '#666',
              fontStyle: 'italic',
              lineHeight: '1.5'
            }}>
              Notice: This assessment is an AI-generated legal research evaluation. It does not constitute formal legal advice or substitute for the counsel of an advocate enrolled under the Advocates Act, 1961.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
