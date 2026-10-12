import React, { useState, useEffect } from 'react';
import { Info, X } from 'lucide-react';

const NOTICE_KEY = 'ax101_services_notice_v1';

/**
 * A minimal, non-blocking informational notice about the Google Fonts CDN request.
 * This is NOT a cookie consent banner (AX101 sets no cookies).
 * It informs users about the one third-party network call made on page load.
 * 
 * Requirements met:
 * - Does not block page use
 * - Can be dismissed
 * - Dismissal is stored so it doesn't re-appear
 * - Keyboard accessible (focus-visible, Escape to dismiss)
 * - Screen-reader compatible (role="status", aria-live="polite")
 */
export default function ServicesNotice() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const dismissed = localStorage.getItem(NOTICE_KEY);
    if (!dismissed) {
      setVisible(true);
    }
  }, []);

  const dismiss = () => {
    localStorage.setItem(NOTICE_KEY, '1');
    setVisible(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') dismiss();
  };

  if (!visible) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      aria-label="Third-party services notice"
      onKeyDown={handleKeyDown}
      style={{
        position: 'fixed',
        bottom: '16px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
        background: 'var(--bg-tertiary)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        maxWidth: '600px',
        width: 'calc(100% - 32px)',
        boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
        fontSize: '12px',
        color: 'var(--text-muted)',
      }}
    >
      <Info
        size={16}
        color="var(--accent-primary)"
        style={{ flexShrink: 0 }}
        aria-hidden="true"
      />
      <p style={{ margin: 0, flex: 1 }}>
        AX101 uses{' '}
        <a
          href="https://fonts.google.com"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: 'var(--accent-primary)' }}
        >
          Google Fonts
        </a>{' '}
        to load typefaces. This is the only third-party network request we make. No cookies are set. No analytics or advertising technologies are used.{' '}
        <a
          href="/cookie-policy"
          style={{ color: 'var(--accent-primary)' }}
        >
          Cookie Policy
        </a>
        {' '}·{' '}
        <a
          href="/privacy-policy"
          style={{ color: 'var(--accent-primary)' }}
        >
          Privacy Policy
        </a>
      </p>
      <button
        onClick={dismiss}
        aria-label="Dismiss services notice"
        style={{
          background: 'none',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--text-muted)',
          cursor: 'pointer',
          padding: '4px',
          display: 'flex',
          alignItems: 'center',
          flexShrink: 0,
        }}
      >
        <X size={14} aria-hidden="true" />
      </button>
    </div>
  );
}
