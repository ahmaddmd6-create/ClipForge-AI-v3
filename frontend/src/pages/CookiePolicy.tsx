import { ShieldCheck } from 'lucide-react';

export default function CookiePolicy() {
  return (
    <div className="container" style={{ maxWidth: '820px' }}>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <ShieldCheck size={26} />
          <h1>Cookie Policy</h1>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Effective date: October 12, 2026</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', fontSize: '0.925rem', lineHeight: 1.6 }}>
        <section className="card">
          <h2>1. Zero Tracking Cookies</h2>
          <p style={{ marginTop: '0.5rem' }}>
            ClipForge AI does not use tracking cookies, advertising trackers, third-party analytics pixels, or behavioral profiling mechanisms.
          </p>
        </section>

        <section className="card">
          <h2>2. Strictly Essential Local Storage</h2>
          <p style={{ marginTop: '0.5rem' }}>
            The application may store temporary UI state (such as the currently active tab or filter selection) directly within your browser's standard <code>localStorage</code> or session memory. This data never leaves your computer.
          </p>
        </section>

        <section className="card">
          <h2>3. Managing Storage Preferences</h2>
          <p style={{ marginTop: '0.5rem' }}>
            Because ClipForge AI employs no non-essential cookies or third-party trackers, a cookie consent banner is neither legally required nor displayed. You can clear your browser's local storage anytime via your browser settings.
          </p>
        </section>
      </div>
    </div>
  );
}
