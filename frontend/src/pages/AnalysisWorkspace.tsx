import React, { useEffect, useState } from 'react';
import { RefreshCw, Play, ArrowLeft, Film } from 'lucide-react';
import { api } from '../api/client';
import type { Job, ClipSummary } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ProgressBar } from '../components/ProgressBar';

interface AnalysisWorkspaceProps {
  jobId: string;
  onNavigate: (tab: string, id?: string) => void;
}

export const AnalysisWorkspace: React.FC<AnalysisWorkspaceProps> = ({ jobId, onNavigate }) => {
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingClipId, setEditingClipId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editStart, setEditStart] = useState(0);
  const [editEnd, setEditEnd] = useState(0);

  const fetchJob = async () => {
    try {
      const data = await api.getJob(jobId);
      setJob(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load job details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJob();
    const interval = setInterval(() => {
      // Keep polling until completed, failed or cancelled
      if (job && !['completed', 'failed', 'cancelled'].includes(job.status)) {
        fetchJob();
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [jobId, job?.status]);

  const handleStartEdit = (clip: ClipSummary) => {
    setEditingClipId(clip.id);
    setEditTitle(clip.title);
    setEditStart(clip.start_time);
    setEditEnd(clip.end_time);
  };

  const handleSaveEdit = async (clipId: string) => {
    if (editStart >= editEnd) {
      alert('Start time must be less than end time.');
      return;
    }
    if ((editEnd - editStart) < 60.0) {
      alert('Clip duration must be at least 60.0 seconds.');
      return;
    }

    try {
      await api.updateClip(clipId, {
        title: editTitle,
        start_time: editStart,
        end_time: editEnd,
      });
      setEditingClipId(null);
      fetchJob();
    } catch (err: any) {
      alert(`Save failed: ${err.message}`);
    }
  };

  if (loading && !job) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
        <p>Loading analysis workspace...</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="container">
        <div className="card" style={{ backgroundColor: 'var(--status-danger-bg)', color: 'var(--status-danger)' }}>
          <p>Job not found: {jobId}</p>
          <button onClick={() => onNavigate('dashboard')} className="btn btn-secondary" style={{ marginTop: '1rem' }}>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button onClick={() => onNavigate('dashboard')} className="btn btn-secondary" style={{ padding: '0.4rem 0.65rem' }}>
            <ArrowLeft size={16} />
            <span>Dashboard</span>
          </button>
          <div>
            <h1>{job.title}</h1>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Job ID: {job.id}</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <StatusBadge status={job.status} />
          <button onClick={fetchJob} className="btn btn-secondary" style={{ padding: '0.4rem 0.65rem' }}>
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {error && (
        <div className="card" style={{ backgroundColor: 'var(--status-danger-bg)', color: 'var(--status-danger)' }}>
          {error}
        </div>
      )}

      {/* Progress Card if in flight */}
      {['queued', 'analyzing', 'clipping', 'rendering'].includes(job.status) && (
        <div className="card" style={{ backgroundColor: 'var(--bg-secondary)' }}>
          <ProgressBar progress={job.progress} statusMessage={job.status_message} />
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Current stage: <strong>{job.stage}</strong>. Processing on CPU. All candidate clips are strictly verified to meet the 60s minimum duration.
          </div>
        </div>
      )}

      {/* Media & Niche Overview */}
      <div className="grid-2">
        {/* Source Media Info */}
        <div className="card">
          <h2>Source Media Information</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.75rem', fontSize: '0.875rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Source Type</span>
              <strong>{job.source_type === 'youtube' ? 'YouTube Stream' : 'Uploaded File'}</strong>
            </div>
            {job.source_asset ? (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Duration</span>
                  <strong>{job.source_asset.duration_seconds.toFixed(1)} seconds</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Resolution</span>
                  <strong>{job.source_asset.width} x {job.source_asset.height}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Frame Rate</span>
                  <strong>{job.source_asset.frame_rate} FPS</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Audio Track</span>
                  <strong>{job.source_asset.has_audio ? `Present (${job.source_asset.audio_codec})` : 'Missing'}</strong>
                </div>
              </>
            ) : (
              <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>Inspecting media streams with FFprobe...</p>
            )}
          </div>
        </div>

        {/* Niche & Audience Info */}
        <div className="card">
          <h2>Niche & Content Classification</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.75rem', fontSize: '0.875rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Detected Niche</span>
              <strong>{job.detected_niche || 'Analyzing transcript...'}</strong>
            </div>
            {job.confidence_score && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Confidence Score</span>
                <strong>{(job.confidence_score * 100).toFixed(0)}%</strong>
              </div>
            )}
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Target Audience</span>
              <span>{job.target_audience || 'Pending analysis'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Optimal Platforms</span>
              <span>{job.suitable_platforms || 'YouTube Shorts, Reels, TikTok'}</span>
            </div>
            {job.key_themes && (
              <div style={{ marginTop: '0.25rem' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem' }}>Key Themes</span>
                <span style={{ fontSize: '0.825rem', color: 'var(--text-primary)' }}>{job.key_themes}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Candidate Clips Table */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2>Selected Clips ({job.clips?.length || 0} of {job.target_clip_count})</h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Each segment satisfies the mandatory minimum duration of 60.0 seconds.
            </p>
          </div>
          {job.status === 'completed' && (
            <button onClick={() => onNavigate('library')} className="btn btn-primary" style={{ fontSize: '0.85rem' }}>
              <Film size={15} />
              <span>View in Library</span>
            </button>
          )}
        </div>

        {job.clips?.length === 0 ? (
          <div style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Candidate clips will appear here once audio transcription and highlight ranking complete.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Clip #</th>
                  <th>Title & Opening Hook</th>
                  <th>Timestamps</th>
                  <th>Duration</th>
                  <th>Viral Score</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {job.clips.map((clip) => {
                  const isEditing = editingClipId === clip.id;
                  return (
                    <tr key={clip.id}>
                      <td style={{ fontWeight: 700 }}>#{clip.clip_index}</td>
                      <td style={{ maxWidth: '320px' }}>
                        {isEditing ? (
                          <input
                            type="text"
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            className="form-input"
                            style={{ padding: '0.35rem 0.5rem', fontSize: '0.85rem' }}
                          />
                        ) : (
                          <>
                            <div style={{ fontWeight: 600 }}>{clip.title}</div>
                            <div style={{ fontSize: '0.785rem', color: 'var(--text-muted)' }}>
                              "{clip.hook}"
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                              {clip.selection_reason}
                            </div>
                          </>
                        )}
                      </td>
                      <td>
                        {isEditing ? (
                          <div style={{ display: 'flex', gap: '0.35rem', alignItems: 'center' }}>
                            <input
                              type="number"
                              step="0.5"
                              value={editStart}
                              onChange={(e) => setEditStart(Number(e.target.value))}
                              className="form-input"
                              style={{ width: '70px', padding: '0.35rem 0.4rem', fontSize: '0.85rem' }}
                            />
                            <span>-</span>
                            <input
                              type="number"
                              step="0.5"
                              value={editEnd}
                              onChange={(e) => setEditEnd(Number(e.target.value))}
                              className="form-input"
                              style={{ width: '70px', padding: '0.35rem 0.4rem', fontSize: '0.85rem' }}
                            />
                          </div>
                        ) : (
                          <span>{clip.start_time.toFixed(1)}s - {clip.end_time.toFixed(1)}s</span>
                        )}
                      </td>
                      <td>
                        <span style={{ fontWeight: 600, color: clip.duration >= 60 ? 'var(--status-success)' : 'var(--status-danger)' }}>
                          {clip.duration.toFixed(1)}s
                        </span>
                      </td>
                      <td>
                        <span style={{ fontWeight: 600 }}>{clip.viral_score}</span> / 100
                      </td>
                      <td>
                        <StatusBadge status={clip.status} />
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        {isEditing ? (
                          <div style={{ display: 'inline-flex', gap: '0.35rem' }}>
                            <button onClick={() => handleSaveEdit(clip.id)} className="btn btn-primary" style={{ padding: '0.3rem 0.55rem', fontSize: '0.75rem' }}>
                              Save
                            </button>
                            <button onClick={() => setEditingClipId(null)} className="btn btn-secondary" style={{ padding: '0.3rem 0.55rem', fontSize: '0.75rem' }}>
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <div style={{ display: 'inline-flex', gap: '0.35rem' }}>
                            {clip.status === 'candidate' && (
                              <button onClick={() => handleStartEdit(clip)} className="btn btn-secondary" style={{ padding: '0.3rem 0.55rem', fontSize: '0.75rem' }}>
                                Edit
                              </button>
                            )}
                            {clip.status === 'completed' && (
                              <button onClick={() => onNavigate('detail', clip.id)} className="btn btn-secondary" style={{ padding: '0.3rem 0.55rem', fontSize: '0.75rem' }}>
                                <Play size={12} />
                                <span>Preview</span>
                              </button>
                            )}
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
