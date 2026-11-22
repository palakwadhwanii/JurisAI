import React, { useState } from 'react';
import { X, Lock, Mail, User, Shield, AlertCircle, ArrowRight, CheckCircle } from 'lucide-react';
import { apiFetch } from '../api/config';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
    const payload = mode === 'login' 
      ? { username_or_email: username, password }
      : { username, email, password, full_name: fullName || username };

    try {
      const res = await apiFetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed. Please check your credentials.');
      }

      onAuthSuccess(data.user, data.token);
      onClose();
      // Reset fields
      setPassword('');
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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
        maxWidth: '440px',
        width: '100%',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        border: '1px solid var(--court-parchment-border)',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          backgroundColor: 'var(--court-navy)',
          padding: '1.25rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          color: '#ffffff'
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
              <Shield size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, color: '#ffffff' }}>
                {mode === 'login' ? 'Sign In to JurisAI' : 'Create JurisAI Account'}
              </h3>
              <p style={{ fontSize: '11.5px', color: '#cbd5e1', margin: '2px 0 0 0' }}>
                {mode === 'login' 
                  ? 'Access your saved case analyses and search history'
                  : 'Save legal evaluations and track your consultation trail'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '4px'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Tab Toggle */}
        <div style={{
          display: 'flex',
          borderBottom: '1px solid var(--court-parchment-border)',
          backgroundColor: '#f8fafc'
        }}>
          <button
            type="button"
            onClick={() => { setMode('login'); setError(null); }}
            style={{
              flex: 1,
              padding: '0.75rem',
              border: 'none',
              background: mode === 'login' ? '#ffffff' : 'transparent',
              borderBottom: mode === 'login' ? '2px solid var(--court-navy)' : 'none',
              color: mode === 'login' ? 'var(--court-navy)' : 'var(--ink-muted)',
              fontWeight: mode === 'login' ? 700 : 500,
              fontSize: '13.5px',
              cursor: 'pointer'
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setMode('register'); setError(null); }}
            style={{
              flex: 1,
              padding: '0.75rem',
              border: 'none',
              background: mode === 'register' ? '#ffffff' : 'transparent',
              borderBottom: mode === 'register' ? '2px solid var(--court-navy)' : 'none',
              color: mode === 'register' ? 'var(--court-navy)' : 'var(--ink-muted)',
              fontWeight: mode === 'register' ? 700 : 500,
              fontSize: '13.5px',
              cursor: 'pointer'
            }}
          >
            Register Free
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} style={{ padding: '1.5rem' }}>
          {error && (
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.5rem',
              padding: '0.75rem 1rem',
              backgroundColor: 'var(--status-alert-bg)',
              border: '1px solid var(--status-alert-border)',
              borderRadius: '6px',
              marginBottom: '1rem',
              color: 'var(--status-alert)',
              fontSize: '12.5px'
            }}>
              <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>{error}</div>
            </div>
          )}

          {/* Full Name (Register only) */}
          {mode === 'register' && (
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--ink-secondary)', marginBottom: '4px' }}>
                Full Name / Legal Designation
              </label>
              <div style={{ position: 'relative' }}>
                <User size={15} color="var(--ink-muted)" style={{ position: 'absolute', left: '10px', top: '10px' }} />
                <input
                  type="text"
                  placeholder="e.g. Adv. Palak Wadhwani"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 10px 8px 32px',
                    borderRadius: '6px',
                    border: '1px solid var(--court-parchment-border)',
                    fontSize: '13px',
                    boxSizing: 'border-box'
                  }}
                />
              </div>
            </div>
          )}

          {/* Username / Email */}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--ink-secondary)', marginBottom: '4px' }}>
              {mode === 'login' ? 'Username or Email' : 'Username'}
            </label>
            <div style={{ position: 'relative' }}>
              <User size={15} color="var(--ink-muted)" style={{ position: 'absolute', left: '10px', top: '10px' }} />
              <input
                type="text"
                required
                placeholder={mode === 'login' ? 'Enter username or email' : 'Choose a unique username'}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 10px 8px 32px',
                  borderRadius: '6px',
                  border: '1px solid var(--court-parchment-border)',
                  fontSize: '13px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>

          {/* Email (Register only) */}
          {mode === 'register' && (
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--ink-secondary)', marginBottom: '4px' }}>
                Email Address
              </label>
              <div style={{ position: 'relative' }}>
                <Mail size={15} color="var(--ink-muted)" style={{ position: 'absolute', left: '10px', top: '10px' }} />
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 10px 8px 32px',
                    borderRadius: '6px',
                    border: '1px solid var(--court-parchment-border)',
                    fontSize: '13px',
                    boxSizing: 'border-box'
                  }}
                />
              </div>
            </div>
          )}

          {/* Password */}
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--ink-secondary)', marginBottom: '4px' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={15} color="var(--ink-muted)" style={{ position: 'absolute', left: '10px', top: '10px' }} />
              <input
                type="password"
                required
                placeholder={mode === 'login' ? 'Enter your password' : 'At least 6 characters'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 10px 8px 32px',
                  borderRadius: '6px',
                  border: '1px solid var(--court-parchment-border)',
                  fontSize: '13px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="btn-legal-primary"
            style={{
              width: '100%',
              padding: '0.65rem 1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              fontSize: '13.5px',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? (
              'Processing...'
            ) : mode === 'login' ? (
              <>Sign In <ArrowRight size={15} /></>
            ) : (
              <>Create Free Account <ArrowRight size={15} /></>
            )}
          </button>

          {/* Privacy Note */}
          <p style={{
            fontSize: '11px',
            color: 'var(--ink-muted)',
            textAlign: 'center',
            marginTop: '1rem',
            marginBottom: 0
          }}>
            Case data is stored securely and linked to your private account history.
          </p>
        </form>
      </div>
    </div>
  );
}

