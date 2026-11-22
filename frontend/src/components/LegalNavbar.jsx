import React from 'react';
import { ArrowRight, BookOpen, Layers, Clock, User, LogOut, LogIn } from 'lucide-react';

export default function LegalNavbar({ 
  viewMode, 
  onNewCase, 
  onGoToWorkspace, 
  hasAnalysis,
  currentUser,
  onOpenAuth,
  onOpenHistory,
  onSignOut
}) {
  return (
    <header style={{
      background: '#ffffff',
      borderBottom: '1px solid var(--court-parchment-border)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: 'var(--shadow-sm)'
    }}>
      <div style={{
        maxWidth: '1240px',
        margin: '0 auto',
        padding: '0.85rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        {/* Brand identity: Clean professional JurisAI mark (No 'AS' confusion) */}
        <div 
          onClick={onNewCase}
          style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}
        >
          {/* Minimal professional legal mark */}
          <div style={{
            width: '34px',
            height: '34px',
            borderRadius: '5px',
            backgroundColor: 'var(--court-navy)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--court-gold-light)',
            flexShrink: 0
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="3" x2="12" y2="21" />
              <line x1="5" y1="7" x2="19" y2="7" />
              <polyline points="5 7 2 13 8 13 5 7" />
              <polyline points="19 7 16 13 22 13 19 7" />
              <line x1="9" y1="21" x2="15" y2="21" />
            </svg>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{
                fontSize: '1.35rem',
                fontWeight: 700,
                color: 'var(--court-navy)',
                letterSpacing: '-0.01em',
                lineHeight: 1
              }}>
                JurisAI
              </span>
              <span className="badge-pill badge-gold" style={{ fontSize: '10px', padding: '1px 6px' }}>
                INDIAN FAMILY LAW
              </span>
            </div>
            <div style={{
              fontSize: '11px',
              color: 'var(--ink-muted)',
              marginTop: '2px'
            }}>
              Constraint-Aware Legal Reasoning Platform
            </div>
          </div>
        </div>

        {/* Center / Navigation Links for Landing Page */}
        {viewMode === 'landing' ? (
          <nav style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            <a 
              href="#problem-section" 
              style={{ textDecoration: 'none', color: 'var(--ink-secondary)', fontSize: '13.5px', fontWeight: 600 }}
            >
              The Problem
            </a>
            <a 
              href="#five-pillars" 
              style={{ textDecoration: 'none', color: 'var(--ink-secondary)', fontSize: '13.5px', fontWeight: 600 }}
            >
              5 Legal Dimensions
            </a>
            <a 
              href="#what-it-provides" 
              style={{ textDecoration: 'none', color: 'var(--ink-secondary)', fontSize: '13.5px', fontWeight: 600 }}
            >
              Deliverables
            </a>
            <a 
              href="#case-input-section" 
              style={{ textDecoration: 'none', color: 'var(--ink-secondary)', fontSize: '13.5px', fontWeight: 600 }}
            >
              Describe Your Case
            </a>
          </nav>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span className="badge-pill badge-navy" style={{ fontSize: '12px' }}>
              <Layers size={13} /> Active Workspace
            </span>
            <span className="badge-pill badge-gold" style={{ fontSize: '12px' }}>
              <BookOpen size={13} /> 12 Central Acts
            </span>
          </div>
        )}

        {/* Right actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          {/* History button if logged in */}
          {currentUser ? (
            <button
              onClick={onOpenHistory}
              className="btn-legal-secondary"
              style={{
                fontSize: '12.5px',
                padding: '0.45rem 0.85rem',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
              title="View your saved case & search history"
            >
              <Clock size={14} color="var(--court-navy)" />
              <span>History</span>
            </button>
          ) : null}

          {/* User profile / Auth button */}
          {currentUser ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '4px 10px',
                borderRadius: '6px',
                backgroundColor: 'var(--court-parchment-gold)',
                border: '1px solid var(--court-parchment-border)',
                fontSize: '12px',
                fontWeight: 600,
                color: 'var(--court-navy)'
              }}>
                <User size={13} />
                <span>{currentUser.full_name || currentUser.username}</span>
              </div>
              <button
                onClick={onSignOut}
                title="Sign Out"
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--ink-muted)',
                  cursor: 'pointer',
                  padding: '5px',
                  display: 'flex',
                  alignItems: 'center'
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--ink-muted)'}
              >
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="btn-legal-secondary"
              style={{
                fontSize: '12.5px',
                padding: '0.45rem 0.85rem',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <LogIn size={14} />
              <span>Sign In</span>
            </button>
          )}

          {viewMode === 'workspace' ? (
            <button 
              onClick={onNewCase} 
              className="btn-legal-secondary"
              style={{ fontSize: '12.5px', padding: '0.45rem 0.85rem' }}
            >
              New Case
            </button>
          ) : hasAnalysis ? (
            <button 
              onClick={onGoToWorkspace} 
              className="btn-legal-gold"
              style={{ fontSize: '12.5px', padding: '0.45rem 0.85rem' }}
            >
              Resume Workspace <ArrowRight size={14} />
            </button>
          ) : (
            <a 
              href="#case-input-section" 
              className="btn-legal-primary"
              style={{ textDecoration: 'none', fontSize: '12.5px', padding: '0.45rem 0.95rem' }}
            >
              Analyze Case <ArrowRight size={14} />
            </a>
          )}
        </div>
      </div>
    </header>
  );
}
