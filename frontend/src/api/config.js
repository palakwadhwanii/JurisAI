/**
 * JurisAI Centralized API Configuration & Client
 *
 * Handles:
 * - Production deployments: Vercel frontend talking to Render backend via VITE_API_URL
 * - Local development: Vite dev proxy (/api -> http://127.0.0.1:8000)
 * - Automatic Bearer token authentication injection
 * - Graceful timeout handling so the UI never hangs indefinitely if the backend is waking up
 */

export const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

/**
 * Returns the full API URL for a given endpoint.
 * If VITE_API_URL is configured (production), prepends it.
 * Otherwise returns the relative endpoint (local dev proxy).
 */
export function getApiUrl(endpoint) {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  if (API_BASE_URL) {
    return `${API_BASE_URL}${cleanEndpoint}`;
  }
  return cleanEndpoint;
}

/**
 * Unified fetch helper that automatically attaches the stored Bearer token,
 * handles custom headers, supports timeouts, and provides fallback in local development.
 */
export async function apiFetch(endpoint, options = {}) {
  const url = getApiUrl(endpoint);
  const token = localStorage.getItem('jurisai_token');

  const headers = {
    ...(options.headers || {})
  };

  if (token && !headers['Authorization'] && !headers['authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // 45s timeout to prevent hanging forever if cloud backend is waking up
  const timeoutMs = options.timeoutMs || 45000;
  const controller = new AbortController();
  const timerId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, {
      ...options,
      headers,
      signal: options.signal || controller.signal
    });
    clearTimeout(timerId);
    return res;
  } catch (err) {
    clearTimeout(timerId);
    if (err.name === 'AbortError') {
      throw new Error('Connection timed out. The backend server might be restarting or waking up; please try again in a moment.');
    }
    // Only in local development fallback to direct localhost:8000 if relative request failed
    if (import.meta.env.DEV && !API_BASE_URL && !url.startsWith('http')) {
      const fallbackUrl = `http://127.0.0.1:8000${url}`;
      return await fetch(fallbackUrl, { ...options, headers });
    }
    throw err;
  }
}
