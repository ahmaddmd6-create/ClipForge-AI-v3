import React, { useEffect, useState } from 'react';
import { Play, Download, Film, RefreshCw, PlusCircle } from 'lucide-react';
import { api } from '../api/client';
import type { ClipDetail } from '../types';

interface ClipLibraryProps {
  onNavigate: (tab: string, clipId?: string) => void;
}

export const ClipLibrary: React.FC<ClipLibraryProps> = ({ onNavigate }) => {
  const [clips, setClips] = useState<ClipDetail[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchClips = async () => {
    try {
      setError(null);
      const data = await api.getClips(undefined, 'completed');
      setClips(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch clips.');
    }
  };

  useEffect(() => {
    fetchClips();
  }, []);

  return (
    <div className="container" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>Clip Library</h1>
          <p style={{ marginTop: '0.25rem' }}>All completed 60s+ short-form vertical clips ready for export and download.</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={fetchClips} className="btn btn-secondary">
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
          <button onClick={() => onNavigate('create')} className="btn btn-primary">
            <PlusCircle size={15} />
            <span>Create clips</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="card" style={{ backgroundColor: 'var(--status-danger-bg)', color: 'var(--status-danger)' }}>
          {error}
        </div>
      )}

      {clips.length === 0 ? (
        <div className="card" style={{ padding: '3.5rem', textAlign: 'center' }}>
          <Film size={36} style={{ color: 'var(--text-muted)', margin: '0 auto 0.75rem' }} />
          <h2>No completed clips yet</h2>
          <p style={{ marginTop: '0.25rem', marginBottom: '1.25rem' }}>
            Completed clips with burnt-in captions will automatically appear here once rendered.
          </p>
          <button onClick={() => onNavigate('create')} className="btn btn-primary">
            <span>Create clips</span>
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
          {clips.map((clip) => (
            <div key={clip.id} className="card" style={{ padding: '0.75rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                {/* Thumbnail Preview Area */}
                <div 
                  onClick={() => onNavigate('detail', clip.id)}
                  style={{
                    width: '100%',
                    aspectRatio: '9/16',
                    maxHeight: '280px',
                    backgroundColor: '#000000',
                    borderRadius: 'var(--radius-sm)',
                    overflow: 'hidden',
                    position: 'relative',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  {clip.thumbnail_url ? (
                    <img 
                      src={clip.thumbnail_url} 
                      alt={clip.title} 
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                    />
                  ) : (
                    <Film size={32} style={{ color: '#ffffff' }} />
                  )}
                  
                  {/* Play Overlay */}
                  <div 
                    style={{
                      position: 'absolute',
                      inset: 0,
                      backgroundColor: 'rgba(0, 0, 0, 0.25)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white'
                    }}
                  >
                    <div style={{ backgroundColor: 'rgba(0, 0, 0, 0.65)', borderRadius: '50%', padding: '0.5rem', display: 'flex' }}>
                      <Play size={20} />
                    </div>
                  </div>

                  <span 
                    style={{
                      position: 'absolute',
                      bottom: '8px',
                      right: '8px',
                      backgroundColor: 'rgba(0, 0, 0, 0.8)',
                      color: '#ffffff',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      padding: '0.15rem 0.4rem',
                      borderRadius: 'var(--radius-sm)'
                    }}
                  >
                    {clip.duration.toFixed(1)}s
                  </span>
                </div>

                <div style={{ marginTop: '0.65rem' }}>
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 600, lineHeight: 1.3 }}>{clip.title}</h3>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    Score: <strong>{clip.viral_score}/100</strong> • {clip.file_size_mb} MB
                  </p>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.75rem' }}>
                <button
                  onClick={() => onNavigate('detail', clip.id)}
                  className="btn btn-secondary"
                  style={{ flex: 1, padding: '0.4rem', fontSize: '0.8rem' }}
                >
                  <Play size={13} />
                  <span>Preview</span>
                </button>
                {clip.video_url && (
                  <a
                    href={clip.video_url}
                    download
                    className="btn btn-primary"
                    style={{ padding: '0.4rem 0.65rem', fontSize: '0.8rem', textDecoration: 'none' }}
                    title="Download MP4"
                  >
                    <Download size={13} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
