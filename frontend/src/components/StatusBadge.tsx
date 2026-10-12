import React from 'react';
import { Clock, Loader2, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const norm = (status || 'queued').toLowerCase();

  const getIcon = () => {
    switch (norm) {
      case 'completed':
        return <CheckCircle2 size={12} />;
      case 'failed':
        return <AlertCircle size={12} />;
      case 'cancelled':
        return <XCircle size={12} />;
      case 'analyzing':
      case 'rendering':
      case 'clipping':
        return <Loader2 size={12} className="spin" />;
      case 'queued':
      default:
        return <Clock size={12} />;
    }
  };

  return (
    <span className={`badge badge-${norm}`}>
      {getIcon()}
      <span>{norm}</span>
    </span>
  );
};
