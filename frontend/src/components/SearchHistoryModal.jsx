import React, { useState, useEffect } from 'react';
import { 
  X, 
  Clock, 
  Search, 
  Trash2, 
  ExternalLink, 
  AlertCircle, 
  CheckCircle2, 
  BookOpen, 
  RefreshCw,
  FileText
} from 'lucide-react';
import { apiFetch } from '../api/config';

export default function SearchHistoryModal({ 
  isOpen, 
  onClose, 
  token, 
  onSelectCase 
}) {
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchFilter, setSearchFilter] = useState('');
  const [restoringId, setRestoringId] = useState(null);

  const fetchHistory = async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch('/api/history', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!res.ok) {
        throw new Error('Failed to load search history.');
      }
      const data = await res.json();
      setHistoryItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && token) {
      fetchHistory();
    }
  }, [isOpen, token]);

  if (!isOpen) return null;

  const handleRestoreCase = async (historyId) => {
    setRestoringId(historyId);
    try {
      const res = await apiFetch(`/api/history/${historyId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!res.ok) throw new Error('Could not load past analysis data.');
      const data = await res.json();
      if (data.analysis_data) {
        onSelectCase(data.analysis_data);
        onClose();
      } else {
        alert('This historical entry has summary notes only and cannot be restored completely.');
      }
    } catch (err) {
      alert(`Error restoring case: ${err.message}`);
    } finally {
      setRestoringId(null);
    }
  };

  const handleDeleteItem = async (historyId, e) => {
    e.stopPropagation();
    try {
      const res = await apiFetch(`/api/history/${historyId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setHistoryItems((prev) => prev.filter((item) => item.id !== historyId));
      }
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to clear your entire search and case history?')) return;
    try {
      const res = await apiFetch('/api/history', {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setHistoryItems([]);
      }
    } catch (err) {
      console.error('Clear error:', err);
    }
  };

  const filteredItems = historyItems.filter((item) => {
    const q = searchFilter.toLowerCase();
    return (
      item.query_text.toLowerCase().includes(q) ||
      (item.case_type && item.case_type.toLowerCase().includes(q)) ||
      (item.summary && item.summary.toLowerCase().includes(q))
    );
  });

  const formatDate = (isoStr) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.65)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        maxWidth: '720px',
        width: '100%',
        maxHeight: '85vh',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        border: '1px solid var(--court-parchment-border)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          backgroundColor: 'var(--court-navy)',
          padding: '1.25rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          color: '#ffffff',
          flexShrink: 0
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '6px',
              backgroundColor: 'rgba(255, 255, 255, 0.12)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--court-gold-light)'
            }}>
              <Clock size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: '#ffffff' }}>
                Your Search & Case History
              </h3>
              <p style={{ fontSize: '11.5px', color: '#cbd5e1', margin: '2px 0 0 0' }}>
                View and reload previously evaluated cases directly into the workspace
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {historyItems.length > 0 && (
              <button
                onClick={handleClearAll}
                className="btn-legal-secondary"
                style={{
                  fontSize: '11.5px',
                  padding: '4px 8px',
                  color: '#ef4444',
                  borderColor: 'rgba(239, 68, 68, 0.4)'
                }}
              >
                Clear All
              </button>
            )}
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Search filter input */}
        <div style={{
          padding: '0.75rem 1.25rem',
          borderBottom: '1px solid var(--court-parchment-border)',
          backgroundColor: '#f8fafc',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <Search size={16} color="var(--ink-muted)" />
          <input
            type="text"
            placeholder="Search within your previous queries..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            style={{
              flex: 1,
              border: 'none',
              background: 'transparent',
              fontSize: '13px',
              outline: 'none',
              color: 'var(--ink-primary)'
            }}
          />
          {searchFilter && (
            <button
              onClick={() => setSearchFilter('')}
              style={{ border: 'none', background: 'transparent', cursor: 'pointer', color: 'var(--ink-muted)', fontSize: '12px' }}
            >
              Clear
            </button>
          )}
        </div>

        {/* History List */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1rem 1.25rem'
        }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--ink-muted)' }}>
              <RefreshCw size={24} className="spin" style={{ marginBottom: '0.5rem', animation: 'spin 1s linear infinite' }} />
              <div>Loading search history...</div>
            </div>
          ) : error ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: 'var(--status-alert)',
              backgroundColor: 'var(--status-alert-bg)',
              padding: '1rem',
              borderRadius: '6px'
            }}>
              <AlertCircle size={18} />
              <div>{error}</div>
            </div>
          ) : filteredItems.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '3rem 1rem',
              color: 'var(--ink-muted)'
            }}>
              <FileText size={36} color="var(--court-parchment-border)" style={{ marginBottom: '0.75rem' }} />
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink-secondary)' }}>
                {searchFilter ? 'No matching history records found.' : 'No search or analysis history yet.'}
              </div>
              <p style={{ fontSize: '12.5px', maxWidth: '360px', margin: '0.5rem auto 0 auto' }}>
                {searchFilter 
                  ? 'Try searching with a different term.'
                  : 'Whenever you analyze a legal case while signed in, it will automatically be saved here so you can review it anytime.'}
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {filteredItems.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleRestoreCase(item.id)}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid var(--court-parchment-border)',
                    borderRadius: '8px',
                    padding: '1rem',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'var(--court-navy)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.06)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--court-parchment-border)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className="badge-pill badge-navy" style={{ fontSize: '11px' }}>
                        {item.case_type || 'Family Law Case'}
                      </span>
                      <span className={`badge-pill ${item.outcome === 'PASS' ? 'badge-pass' : 'badge-warn'}`} style={{ fontSize: '10.5px' }}>
                        {item.outcome}
                      </span>
                    </div>
                    <div style={{ fontSize: '11.5px', color: 'var(--ink-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={12} />
                      {formatDate(item.created_at)}
                    </div>
                  </div>

                  {/* Query preview */}
                  <div style={{
                    fontSize: '13px',
                    color: 'var(--ink-primary)',
                    lineHeight: 1.4,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>
                    {item.query_text}
                  </div>

                  {/* Actions */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginTop: '0.25rem',
                    paddingTop: '0.5rem',
                    borderTop: '1px dashed var(--court-parchment-border)'
                  }}>
                    <span style={{
                      fontSize: '12px',
                      color: 'var(--court-navy)',
                      fontWeight: 600,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}>
                      <ExternalLink size={13} />
                      {restoringId === item.id ? 'Restoring...' : 'Open in Workspace'}
                    </span>
                    <button
                      type="button"
                      onClick={(e) => handleDeleteItem(item.id, e)}
                      title="Delete from history"
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--ink-muted)',
                        cursor: 'pointer',
                        padding: '4px',
                        borderRadius: '4px'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                      onMouseLeave={(e) => e.currentTarget.style.color = 'var(--ink-muted)'}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '0.75rem 1.25rem',
          borderTop: '1px solid var(--court-parchment-border)',
          backgroundColor: '#f8fafc',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '12px',
          color: 'var(--ink-muted)'
        }}>
          <div>{historyItems.length} saved case{historyItems.length === 1 ? '' : 's'}</div>
          <button
            onClick={onClose}
            className="btn-legal-secondary"
            style={{ fontSize: '12px', padding: '4px 12px' }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

