import React, { useState, useRef } from 'react';

export default function DocumentUpload({ onDocumentExtracted, uploadedDocs }) {
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/upload-document', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        throw new Error(`Upload failed with status ${res.status}`);
      }
      const data = await res.json();
      onDocumentExtracted(data);
    } catch (err) {
      setErrorMsg(`Document parsing notice: ${err.message}. (You can also paste the text directly into case intake).`);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <section id="document-upload" style={{ marginBottom: '2.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '0.8rem' }}>
        <div>
          <span className="notebook-tag tag-ink" style={{ marginRight: '0.5rem' }}>Component 2</span>
          <span className="mono" style={{ fontSize: '13px', color: 'var(--text-muted)' }}>document-upload.tsx</span>
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-faint)', fontStyle: 'italic' }}>
          Supports .txt, .pdf, or court orders
        </div>
      </div>

      <div style={{
        border: '1px dashed var(--border-line)',
        backgroundColor: 'var(--bg-subtle)',
        padding: '1.2rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.8rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.8rem' }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '2px' }}>
              Attach Supporting Legal Documents / Evidence
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
              Upload settlement agreements, joint petitions, FIRs, or marriage certificates for the Evidence Agent.
            </div>
          </div>
          <div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".txt,.pdf,.md"
              style={{ display: 'none' }}
              id="doc-upload-input"
            />
            <label
              htmlFor="doc-upload-input"
              className="btn-secondary"
              style={{ display: 'inline-block', cursor: 'pointer', fontSize: '12px', background: '#fff' }}
            >
              {uploading ? 'Extracting Text...' : '+ Select Legal Document'}
            </label>
          </div>
        </div>

        {errorMsg && (
          <div style={{ fontSize: '12px', color: 'var(--accent-terra)', background: 'var(--accent-terra-bg)', padding: '6px 10px', border: '1px solid #f0c5b5' }}>
            {errorMsg}
          </div>
        )}

        {/* List of uploaded documents */}
        {uploadedDocs && uploadedDocs.length > 0 && (
          <div style={{ borderTop: '1px solid var(--border-line)', paddingTop: '0.8rem', marginTop: '0.2rem' }}>
            <div style={{ fontSize: '12px', textTransform: 'uppercase', fontFamily: 'var(--mono-font)', color: 'var(--text-faint)', marginBottom: '0.4rem' }}>
              Attached Document Evidence:
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {uploadedDocs.map((doc, idx) => (
                <div
                  key={idx}
                  style={{
                    background: '#fff',
                    border: '1px solid var(--border-line)',
                    padding: '8px 12px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '13px'
                  }}
                >
                  <div>
                    <span className="mono" style={{ fontWeight: 600, marginRight: '0.5rem' }}>📄 {doc.filename}</span>
                    <span style={{ color: 'var(--text-faint)', fontSize: '12px' }}>({doc.char_count} characters)</span>
                  </div>
                  <div>
                    {doc.detected_entities && doc.detected_entities.map((ent, eIdx) => (
                      <span key={eIdx} className="notebook-tag tag-sage" style={{ marginLeft: '4px', fontSize: '10px' }}>
                        {ent}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
