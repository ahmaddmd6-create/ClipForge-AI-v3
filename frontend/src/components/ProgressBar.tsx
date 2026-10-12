import React from 'react';

interface ProgressBarProps {
  progress: number;
  stage?: string;
  statusMessage?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress, stage, statusMessage }) => {
  const boundedProgress = Math.min(100, Math.max(0, progress));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
        <span>{statusMessage || stage || 'Processing...'}</span>
        <span style={{ fontWeight: 600 }}>{boundedProgress}%</span>
      </div>
      <div 
        className="progress-container"
        role="progressbar"
        aria-valuenow={boundedProgress}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={statusMessage || 'Job Progress'}
      >
        <div className="progress-bar" style={{ width: `${boundedProgress}%` }} />
      </div>
    </div>
  );
};
