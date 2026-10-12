import React from 'react';
import { AlertCircle, ArrowLeft } from 'lucide-react';

interface NotFoundProps {
  onNavigate: (tab: string) => void;
}

export const NotFound: React.FC<NotFoundProps> = ({ onNavigate }) => {
  return (
    <div className="container" style={{ textAlign: 'center', padding: '5rem 1rem' }}>
      <div style={{ color: 'var(--text-muted)', marginBottom: '1rem', display: 'flex', justifyContent: 'center' }}>
        <AlertCircle size={44} />
      </div>
      <h1 style={{ marginBottom: '0.5rem' }}>Page Not Found</h1>
      <p style={{ maxWidth: '440px', margin: '0 auto 1.5rem' }}>
        The requested page or resource could not be found. You can return to the main dashboard anytime.
      </p>
      <button onClick={() => onNavigate('dashboard')} className="btn btn-primary">
        <ArrowLeft size={16} />
        <span>Return to Dashboard</span>
      </button>
    </div>
  );
};

export default NotFound;
