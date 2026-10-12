import React from 'react';

interface FooterProps {
  onNavigate: (tab: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer style={{ borderTop: '1px solid var(--border-color)', marginTop: '4rem', padding: '2rem 1rem', backgroundColor: 'var(--bg-primary)' }}>
      <div className="container" style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        <div>
          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>ClipForge AI</span> — Local Video Intelligence Workstation (CPU Edition)
        </div>
        <nav aria-label="Legal Navigation" style={{ display: 'flex', gap: '1.25rem' }}>
          <button onClick={() => onNavigate('privacy')} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', textDecoration: 'underline' }}>
            Privacy Policy
          </button>
          <button onClick={() => onNavigate('terms')} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', textDecoration: 'underline' }}>
            Terms & Conditions
          </button>
          <button onClick={() => onNavigate('cookies')} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', textDecoration: 'underline' }}>
            Cookie Policy
          </button>
          <button onClick={() => onNavigate('refunds')} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', textDecoration: 'underline' }}>
            Refund Information
          </button>
        </nav>
      </div>
    </footer>
  );
};

export default Footer;
