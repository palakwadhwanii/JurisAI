import React, { useState, useRef } from 'react';
import { getApiUrl } from '../api/config';
import { 
  Send, 
  Paperclip, 
  X, 
  FileCheck2,
  Loader2,
  FileText,
  Sparkles,
  Check
} from 'lucide-react';

export default function CaseInputSection({
  caseText,
  setCaseText,
  onAnalyze,
  loading,
  uploadedDocs,
  onDocumentExtracted,
  onRemoveDoc,
  apiError
}) {
  const [uploading, setUploading] = useState(false);
  const [uploadNotice, setUploadNotice] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);

  // Quick case scenario helpers for 1-click test input
  const sampleScenarios = [
    {
      label: 'Mutual Consent Waiver',
      text: 'I got married in 2020 under the Hindu Marriage Act. My husband and I have been living separately for over 2 years due to severe incompatibility. We have now reached a comprehensive mutual settlement agreement covering alimony and custody. We want to dissolve our marriage under Section 13B and seek immediate waiver of the 6-month cooling-off period under Supreme Court rulings.'
    },
    {
      label: 'Contested Cruelty & False FIR',
      text: 'Marriage solemnized in 2018 under Hindu rites. After persistent marital discord, wife left the matrimonial home in 2021 and filed false criminal complaints under Section 498A IPC against husband and elderly parents. The criminal trial concluded with a complete honorable acquittal observing false allegations. Husband now seeks dissolution of marriage on the grounds of mental cruelty under Section 13(1)(ia).'
    },
    {
      label: 'PWDVA Shared Household',
      text: 'Applicant married respondent in 2019 and resided in a joint family household standing in the name of the father-in-law. Following marital discord and eviction, applicant seeks protection orders and right of residence in the shared household under Section 17 and Section 19 of the Protection of Women from Domestic Violence Act, 2005.'
    }
  ];

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setUploadNotice(null);

    const isTextFile = file.name.endsWith('.txt') || file.name.endsWith('.md') || file.name.endsWith('.rtf') || file.name.endsWith('.json') || file.type.startsWith('text/');

    // 1. Client-side immediate file reader for text documents
    if (isTextFile) {
      try {
        const reader = new FileReader();
        reader.onload = (event) => {
          const content = event.target.result;
          const docData = {
            filename: file.name,
            extracted_text: content,
            char_count: content.length,
            detected_entities: []
          };

          onDocumentExtracted(docData);

          // Automatically insert extracted text into the case description!
          if (!caseText.trim()) {
            setCaseText(content);
          } else {
            setCaseText((prev) => prev + `\n\n=== ATTACHED DOCUMENT: ${file.name} ===\n` + content);
          }

          setUploadNotice(`Loaded "${file.name}" (${content.length} characters extracted and added to case description).`);
          setUploading(false);
        };

        reader.onerror = () => {
          throw new Error('Failed to read file contents');
        };

        reader.readAsText(file);
        if (fileInputRef.current) fileInputRef.current.value = '';
        return;
      } catch (err) {
        console.warn('Client FileReader fallback failed, attempting backend upload:', err);
      }
    }

    // 2. Backend upload for PDF and complex documents
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(getApiUrl('/api/upload-document'), {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        throw new Error(`Upload error: status ${res.status}`);
      }

      const data = await res.json();
      onDocumentExtracted(data);

      // Automatically insert extracted text into case description!
      if (!caseText.trim()) {
        setCaseText(data.extracted_text);
      } else {
        setCaseText((prev) => prev + `\n\n=== ATTACHED DOCUMENT: ${data.filename} ===\n` + data.extracted_text);
      }

      setUploadNotice(`Loaded "${data.filename}" (${data.char_count} characters extracted and added to case description).`);
    } catch (err) {
      setUploadError(`Could not extract document automatically: ${err.message}. You can also paste your document text directly into the description box.`);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const isReadyToAnalyze = caseText.trim().length > 0 || (uploadedDocs && uploadedDocs.length > 0);

  return (
    <section id="case-input-section" style={{
      background: '#ffffff',
      borderTop: '1px solid var(--court-parchment-border)',
      borderBottom: '1px solid var(--court-parchment-border)',
      padding: '4rem 1.5rem',
      position: 'relative'
    }}>
      <div style={{ maxWidth: '880px', margin: '0 auto' }}>
        {/* Section Header */}
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <h2 style={{ fontSize: '2.3rem', marginBottom: '0.4rem', fontWeight: 700 }}>
            Describe Your Case
          </h2>

          <p style={{
            fontSize: '16px',
            color: 'var(--court-gold-dark)',
            fontWeight: 600,
            maxWidth: '680px',
            margin: '0 auto'
          }}>
            Describe your legal situation in your own words. You don't need to know legal terminology.
          </p>
        </div>

        {/* Quick test scenarios helper chips */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
          flexWrap: 'wrap',
          justifyContent: 'center',
          marginBottom: '1.25rem'
        }}>
          <span style={{ fontSize: '12px', color: 'var(--ink-muted)', fontWeight: 600 }}>
            Quick test scenario:
          </span>
          {sampleScenarios.map((sc, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setCaseText(sc.text);
                setUploadNotice(`Loaded sample scenario: "${sc.label}". Click "Analyze Case" below.`);
              }}
              className="btn-legal-secondary"
              style={{
                fontSize: '12px',
                padding: '4px 10px',
                backgroundColor: '#ffffff'
              }}
            >
              {sc.label}
            </button>
          ))}
        </div>

        {/* Upload Success or Notice Alert */}
        {uploadNotice && (
          <div style={{
            background: 'var(--status-pass-bg)',
            border: '1px solid var(--status-pass-border)',
            borderRadius: '4px',
            padding: '10px 14px',
            marginBottom: '1rem',
            fontSize: '13.5px',
            color: 'var(--status-pass)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.5rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Check size={16} />
              <span>{uploadNotice}</span>
            </div>
            <button
              onClick={() => setUploadNotice(null)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--status-pass)' }}
            >
              <X size={14} />
            </button>
          </div>
        )}

        {/* API Error Alert */}
        {apiError && (
          <div style={{
            background: 'var(--status-alert-bg)',
            border: '1px solid var(--status-alert-border)',
            borderLeft: '4px solid var(--status-alert)',
            borderRadius: '4px',
            padding: '12px 16px',
            marginBottom: '1rem',
            fontSize: '13.5px',
            color: 'var(--status-alert)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.5rem'
          }}>
            <span>{apiError}</span>
          </div>
        )}

        {/* Clean card-based case intake interface */}
        <div style={{
          background: '#ffffff',
          border: '1px solid var(--court-parchment-border)',
          borderRadius: '8px',
          boxShadow: 'var(--shadow-md)',
          overflow: 'hidden'
        }}>
          {/* Main Textarea: Editable, accepts text or extracted documents */}
          <div style={{ padding: '1.25rem 1.25rem 0.5rem 1.25rem' }}>
            <textarea
              id="case-narrative-input"
              value={caseText}
              onChange={(e) => setCaseText(e.target.value)}
              placeholder="Tell JurisAI what happened..."
              rows={8}
              style={{
                width: '100%',
                border: 'none',
                outline: 'none',
                resize: 'vertical',
                fontSize: '15px',
                lineHeight: 1.6,
                fontFamily: 'var(--font-family-base)',
                color: 'var(--ink-primary)',
                background: 'transparent'
              }}
            />
          </div>

          {/* Uploaded Documents List */}
          {uploadedDocs && uploadedDocs.length > 0 && (
            <div style={{
              padding: '0.65rem 1.25rem',
              borderTop: '1px solid var(--court-parchment-subtle)',
              background: '#faf9f5',
              display: 'flex',
              gap: '0.6rem',
              flexWrap: 'wrap',
              alignItems: 'center'
            }}>
              <span style={{ fontSize: '11.5px', color: 'var(--ink-muted)', fontWeight: 600 }}>
                Attached Files:
              </span>
              {uploadedDocs.map((doc, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    background: '#ffffff',
                    border: '1px solid var(--court-parchment-border)',
                    padding: '4px 10px',
                    borderRadius: '4px',
                    fontSize: '12.5px'
                  }}
                >
                  <FileCheck2 size={14} color="var(--status-pass)" />
                  <span style={{ fontWeight: 600, color: 'var(--court-navy)' }}>{doc.filename}</span>
                  <span style={{ color: 'var(--ink-muted)', fontSize: '11px' }}>({doc.char_count} chars)</span>
                  <button
                    type="button"
                    onClick={() => onRemoveDoc(idx)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '0 2px', display: 'flex', alignItems: 'center' }}
                  >
                    <X size={13} color="var(--ink-muted)" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Bottom Toolbar: Upload trigger & Analyze Case Action */}
          <div style={{
            padding: '0.85rem 1.25rem',
            background: 'var(--court-parchment-subtle)',
            borderTop: '1px solid var(--court-parchment-border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '0.75rem'
          }}>
            {/* Left: Upload Document */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.pdf,.doc,.docx,.rtf,.md"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current && fileInputRef.current.click()}
                disabled={uploading}
                className="btn-legal-secondary"
                style={{ fontSize: '13px', padding: '0.5rem 1rem' }}
              >
                <Paperclip size={14} />
                {uploading ? 'Extracting File...' : 'Attach Document (.pdf, .txt)'}
              </button>

              <span style={{ fontSize: '12px', color: 'var(--ink-muted)' }}>
                {caseText.length} characters
              </span>
            </div>

            {/* Right: Analyze Case Button */}
            <div>
              <button
                id="analyze-case-btn"
                onClick={onAnalyze}
                disabled={loading || !isReadyToAnalyze}
                className="btn-legal-primary"
                style={{ fontSize: '14.5px', padding: '0.7rem 1.8rem', fontWeight: 600 }}
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="pulsing-indicator" />
                    Analyzing Case...
                  </>
                ) : (
                  <>
                    Analyze Case
                    <Send size={14} />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
