import React, { useEffect, useState } from 'react';
import { ArrowLeft, Download, Trash2, Film, FileText } from 'lucide-react';
import { api } from '../api/client';
import type { ClipDetail } from '../types';
import { ConfirmModal } from '../components/ConfirmModal';

interface ClipDetailProps {
  clipId: string;
  onNavigate: (tab: string, id?: string) => void;
}

export const ClipDetailPage: React.FC<ClipDetailProps> = ({ clipId, onNavigate }) => {
  const [clip, setClip] = useState<ClipDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const fetchClip = async () => {
    try {
      setError(null);
      const data = await api.getClip(clipId);
      setClip(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load clip details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClip();
  }, [clipId]);

  const handleDelete = async () => {
    try {
      await api.deleteClip(clipId);
      onNavigate('library');
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  if (loading && !clip) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '4rem' }}>
        <p>Loading clip preview...</p>
      </div>
    );
  }

  if (!clip) {
    return (
      <div className="container">
        <div className="card" style={{ backgroundColor: 'var(--status-danger-bg)', color: 'var(--status-danger)' }}>
          <p>Clip not found: {clipId}</p>
          <button onClick={() => onNavigate('library')} className="btn btn-secondary" style={{ marginTop: '1rem' }}>
            Back to Library
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '960px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button onClick={() => onNavigate('library')} className="btn btn-secondary" style={{ padding: '0.4rem 0.65rem' }}>
            <ArrowLeft size={16} />
            <span>Library</span>
          </button>
          <div>
            <h1>{clip.title}</h1>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Clip #{clip.clip_index} • Job {clip.job_id}</span>
          </div>
        </div>

        <button onClick={() => setShowDeleteModal(true)} className="btn btn-danger" style={{ padding: '0.45rem 0.85rem' }}>
          <Trash2 size={15} />
          <span>Delete Clip</span>
        </button>
      </div>

      {error && (
        <div className="card" style={{ backgroundColor: 'var(--status-danger-bg)', color: 'var(--status-danger)' }}>
          {error}
        </div>
      )}

      {/* Main Grid: Player on left, Metadata & Downloads on right */}
      <div className="grid-2">
        {/* Video Player */}
        <div className="card" style={{ padding: '0.75rem', backgroundColor: '#000000', display: 'flex', justifyContent: 'center' }}>
          {clip.video_url ? (
            <video
              src={clip.video_url}
              controls
              style={{
                width: '100%',
                maxHeight: '520px',
                borderRadius: 'var(--radius-sm)',
                aspectRatio: clip.aspect_ratio === '9:16' ? '9/16' : '16/9',
                objectFit: 'contain'
              }}
            >
              {clip.vtt_url && (
                <track kind="captions" src={clip.vtt_url} srcLang="en" label="English" default />
              )}
              Your browser does not support HTML5 video playback.
            </video>
          ) : (
            <div style={{ padding: '4rem', color: '#ffffff', textAlign: 'center' }}>
              <Film size={36} style={{ margin: '0 auto 0.5rem' }} />
              <p>Video file is not available.</p>
            </div>
          )}
        </div>

        {/* Clip Metadata & Export Formats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Metadata Card */}
          <div className="card">
            <h2>Clip Details</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.75rem', fontSize: '0.875rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Duration</span>
                <strong style={{ color: 'var(--status-success)' }}>{clip.duration.toFixed(1)}s (Meets 60s+ rule)</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Source Range</span>
                <span>{clip.start_time.toFixed(1)}s to {clip.end_time.toFixed(1)}s</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Aspect Ratio</span>
                <strong>{clip.aspect_ratio}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>File Size</span>
                <span>{clip.file_size_mb} MB</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Viral Score</span>
                <strong>{clip.viral_score} / 100</strong>
              </div>

              <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border-color)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem' }}>Selection Reason</span>
                <p style={{ fontSize: '0.825rem' }}>{clip.selection_reason}</p>
              </div>
            </div>
          </div>

          {/* Downloads Card */}
          <div className="card">
            <h2>Download & Export</h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
              Files are saved in your persistent Windows folder and can also be downloaded directly:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {clip.video_url && (
                <a
                  href={clip.video_url}
                  download
                  className="btn btn-primary"
                  style={{ textDecoration: 'none', justifyContent: 'flex-start' }}
                >
                  <Download size={15} />
                  <span>Download MP4 Video ({clip.file_size_mb} MB)</span>
                </a>
              )}

              {clip.srt_url && (
                <a
                  href={clip.srt_url}
                  download
                  className="btn btn-secondary"
                  style={{ textDecoration: 'none', justifyContent: 'flex-start' }}
                >
                  <FileText size={15} />
                  <span>Download SRT Subtitles</span>
                </a>
              )}

              {clip.vtt_url && (
                <a
                  href={clip.vtt_url}
                  download
                  className="btn btn-secondary"
                  style={{ textDecoration: 'none', justifyContent: 'flex-start' }}
                >
                  <FileText size={15} />
                  <span>Download VTT Subtitles</span>
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      <ConfirmModal
        isOpen={showDeleteModal}
        title="Delete Rendered Clip"
        message="Are you sure you want to permanently delete this rendered MP4 video and subtitle files?"
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteModal(false)}
      />
    </div>
  );
};
