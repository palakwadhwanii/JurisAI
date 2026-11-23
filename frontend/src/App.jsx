import React, { useState, useEffect } from 'react';
import LegalNavbar from './components/LegalNavbar';
import LandingHero from './components/LandingHero';
import CaseInputSection from './components/CaseInputSection';
import AgentProgressModal from './components/AgentProgressModal';
import WorkspaceSidebar from './components/WorkspaceSidebar';
import WorkspaceMainContent from './components/WorkspaceMainContent';
import PdfReportTemplate from './components/PdfReportTemplate';
import AuthModal from './components/AuthModal';
import SearchHistoryModal from './components/SearchHistoryModal';
import { apiFetch } from './api/config';

export default function App() {
  const [viewMode, setViewMode] = useState('landing'); // 'landing' | 'workspace'
  const [activeSection, setActiveSection] = useState('overview');
  
  // Case description initially empty as requested in brief
  const [caseText, setCaseText] = useState('');
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [pdfModalOpen, setPdfModalOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  // Authentication & History State
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('jurisai_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [authToken, setAuthToken] = useState(() => {
    return localStorage.getItem('jurisai_token') || null;
  });
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);

  // Auto-warm Render backend on initial app load to minimize free-tier cold start latency
  useEffect(() => {
    apiFetch('/api/health').catch(() => {});
  }, []);

  // Validate session on app launch
  useEffect(() => {
    const verifyToken = async () => {
      if (!authToken) return;
      try {
        const res = await apiFetch('/api/auth/me', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (res.ok) {
          const user = await res.json();
          setCurrentUser(user);
          localStorage.setItem('jurisai_user', JSON.stringify(user));
        } else if (res.status === 401) {
          // Token expired
          handleSignOut();
        }
      } catch (err) {
        console.warn('Session verification skipped:', err);
      }
    };
    verifyToken();
  }, [authToken]);

  const handleAuthSuccess = (user, token) => {
    setCurrentUser(user);
    setAuthToken(token);
    localStorage.setItem('jurisai_user', JSON.stringify(user));
    localStorage.setItem('jurisai_token', token);
  };

  const handleSignOut = async () => {
    if (authToken) {
      try {
        await apiFetch('/api/auth/logout', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${authToken}` }
        }).catch(() => {});
      } catch {}
    }
    setCurrentUser(null);
    setAuthToken(null);
    localStorage.removeItem('jurisai_user');
    localStorage.removeItem('jurisai_token');
  };

  const handleSelectHistoryCase = (restoredData) => {
    setAnalysisData(restoredData);
    setViewMode('workspace');
    setActiveSection('overview');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDocumentExtracted = (docData) => {
    setUploadedDocs((prev) => [...prev, docData]);
  };

  const handleRemoveDoc = (index) => {
    setUploadedDocs((prev) => prev.filter((_, i) => i !== index));
  };

  const handleScrollToInput = () => {
    const el = document.getElementById('case-input-section');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleAnalyze = async () => {
    const textToAnalyze = caseText.trim() || (uploadedDocs && uploadedDocs.length > 0 ? uploadedDocs.map((d) => d.extracted_text).join('\n\n') : '');
    if (!textToAnalyze) return;

    setLoading(true);
    setErrorMessage(null);

    const payload = {
      case_text: textToAnalyze,
      uploaded_documents: uploadedDocs.map((d) => d.extracted_text)
    };

    const headers = {
      'Content-Type': 'application/json',
      ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
    };

    try {
      const res = await apiFetch('/api/analyze', {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error ${res.status}`);
      }

      const data = await res.json();
      setAnalysisData(data);
      
      // Persist to local storage history as bulletproof client-side cache
      try {
        const localHistory = JSON.parse(localStorage.getItem('jurisai_local_history') || '[]');
        const summaryText = textToAnalyze.slice(0, 140) + (textToAnalyze.length > 140 ? '...' : '');
        const newEntry = {
          id: Date.now(),
          analysis_id: data.analysis_id || `analysis-${Date.now()}`,
          query_text: textToAnalyze,
          case_type: data.case_state?.case_type || 'Legal Case Analysis',
          outcome: data.outcome || 'PASS',
          summary: summaryText,
          created_at: new Date().toISOString(),
          analysis_data: data
        };
        const updatedHistory = [newEntry, ...localHistory.filter(h => h.analysis_id !== newEntry.analysis_id)].slice(0, 50);
        localStorage.setItem('jurisai_local_history', JSON.stringify(updatedHistory));
      } catch (e) {
        console.warn('Could not cache analysis to localStorage:', e);
      }

      // Transition within the same page into the Case Analysis Workspace
      setViewMode('workspace');
      setActiveSection('overview');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setErrorMessage(`Analysis failed: ${err.message}. Please verify the backend service.`);
    } finally {
      setLoading(false);
    }
  };

  const handleNewCase = () => {
    setViewMode('landing');
    setCaseText('');
    setUploadedDocs([]);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleGoToWorkspace = () => {
    setViewMode('workspace');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCopyBrief = () => {
    if (analysisData?.final_judgment) {
      navigator.clipboard.writeText(analysisData.final_judgment);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="jurisai-app">
      {/* Top Navbar with Auth & History triggers */}
      <LegalNavbar
        viewMode={viewMode}
        onNewCase={handleNewCase}
        onGoToWorkspace={handleGoToWorkspace}
        hasAnalysis={!!analysisData}
        currentUser={currentUser}
        onOpenAuth={() => setAuthModalOpen(true)}
        onOpenHistory={() => setHistoryModalOpen(true)}
        onSignOut={handleSignOut}
      />

      {/* Error alert banner if any */}
      {errorMessage && (
        <div style={{
          background: 'var(--status-alert-bg)',
          borderBottom: '1px solid var(--status-alert-border)',
          padding: '12px 24px',
          fontSize: '13.5px',
          color: 'var(--status-alert)',
          textAlign: 'center'
        }}>
          {errorMessage}
        </div>
      )}

      {/* VIEW 1: LANDING & CASE INPUT */}
      {viewMode === 'landing' && (
        <>
          <LandingHero onScrollToInput={handleScrollToInput} />
          
          <CaseInputSection
            caseText={caseText}
            setCaseText={setCaseText}
            onAnalyze={handleAnalyze}
            loading={loading}
            uploadedDocs={uploadedDocs}
            onDocumentExtracted={handleDocumentExtracted}
            onRemoveDoc={handleRemoveDoc}
            apiError={errorMessage}
          />
        </>
      )}

      {/* VIEW 2: CASE ANALYSIS WORKSPACE (In-page transition) */}
      {viewMode === 'workspace' && analysisData && (
        <div className="workspace-container">
          {/* Left Sidebar */}
          <WorkspaceSidebar
            activeSection={activeSection}
            onSelectSection={setActiveSection}
            analysisData={analysisData}
            onDownloadPdf={() => setPdfModalOpen(true)}
            onOpenHistory={() => setHistoryModalOpen(true)}
          />

          {/* Main Content Area */}
          <WorkspaceMainContent
            activeSection={activeSection}
            analysisData={analysisData}
            onDownloadPdf={() => setPdfModalOpen(true)}
            onCopyBrief={handleCopyBrief}
            copied={copied}
            onSelectSection={setActiveSection}
          />
        </div>
      )}

      {/* Live 8-Stage Progress Tracker Modal */}
      <AgentProgressModal active={loading} />

      {/* Full PDF Report & Export Modal */}
      <PdfReportTemplate
        analysisData={analysisData}
        isOpen={pdfModalOpen}
        onClose={() => setPdfModalOpen(false)}
      />

      {/* Authentication Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      {/* Search & Case History Modal */}
      <SearchHistoryModal
        isOpen={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
        token={authToken}
        onSelectCase={handleSelectHistoryCase}
      />

      {/* Footer Colophon */}
      <footer style={{
        backgroundColor: '#ffffff',
        borderTop: '1px solid var(--court-parchment-border)',
        padding: '2rem 1.5rem',
        textAlign: 'center',
        fontSize: '13px',
        color: 'var(--ink-muted)'
      }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            JurisAI: 12 Central Acts : 91 Supreme Court Judgments : Multi-Agent Legal Reasoning
          </div>
          <div>
            100% Grounded Citations. Constraint-Aware Case Analysis.
          </div>
        </div>
      </footer>
    </div>
  );
}
