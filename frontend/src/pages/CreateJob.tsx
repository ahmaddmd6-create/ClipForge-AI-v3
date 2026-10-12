import React, { useState } from 'react';
import { PlusCircle, Video, Upload, Settings2, AlertCircle } from 'lucide-react';
import { api } from '../api/client';

interface CreateJobProps {
  onJobCreated: (jobId: string) => void;
}

export const CreateJob: React.FC<CreateJobProps> = ({ onJobCreated }) => {
  const [sourceType, setSourceType] = useState<'youtube' | 'upload'>('youtube');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [rightsDeclared, setRightsDeclared] = useState(false);

  // Settings
  const [clipCount, setClipCount] = useState(5);
  const [minDuration, setMinDuration] = useState(60);
  const [targetDuration, setTargetDuration] = useState(75);
  const maxDuration = 90;
  const [aspectRatio, setAspectRatio] = useState('9:16');
  const [subtitleStyle, setSubtitleStyle] = useState('hormozi_yellow');
  const [burnSubtitles, setBurnSubtitles] = useState(true);
  const backgroundMusic = 'none';
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!rightsDeclared) {
      setError('You must confirm source authorization and rights before starting processing.');
      return;
    }

    if (sourceType === 'youtube' && !youtubeUrl.trim()) {
      setError('Please provide a valid YouTube URL.');
      return;
    }

    if (sourceType === 'upload' && !selectedFile) {
      setError('Please select a local video file to upload.');
      return;
    }

    if (minDuration < 60) {
      setError('Minimum clip duration cannot be less than 60.0 seconds.');
      return;
    }

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('source_type', sourceType);
      formData.append('rights_declared', 'true');
      formData.append('target_clip_count', String(clipCount));
      formData.append('min_duration', String(minDuration));
      formData.append('target_duration', String(targetDuration));
      formData.append('max_duration', String(maxDuration));
      formData.append('aspect_ratio', aspectRatio);
      formData.append('subtitle_style', subtitleStyle);
      formData.append('burn_subtitles', String(burnSubtitles));
      if (backgroundMusic !== 'none') {
        formData.append('background_music', backgroundMusic);
      }

      if (sourceType === 'youtube') {
        formData.append('youtube_url', youtubeUrl.trim());
      } else if (selectedFile) {
        formData.append('file', selectedFile);
      }

      const job = await api.createJob(formData);
      onJobCreated(job.id);
    } catch (err: any) {
      setError(err.message || 'Failed to create job.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '780px' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1>Create clips</h1>
        <p style={{ marginTop: '0.25rem' }}>
          Provide an authorized YouTube link or upload a local video to extract five distinct vertical clips of at least 60 seconds each.
        </p>
      </div>

      {error && (
        <div className="card" style={{ backgroundColor: 'var(--status-danger-bg)', borderColor: '#fecaca', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-danger)', marginBottom: '1.25rem' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Source Selection Card */}
        <div className="card">
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <button
              type="button"
              onClick={() => { setSourceType('youtube'); setError(null); }}
              className={`btn ${sourceType === 'youtube' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1 }}
            >
              <Video size={16} />
              <span>YouTube URL</span>
            </button>
            <button
              type="button"
              onClick={() => { setSourceType('upload'); setError(null); }}
              className={`btn ${sourceType === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1 }}
            >
              <Upload size={16} />
              <span>Local Video File</span>
            </button>
          </div>

          {sourceType === 'youtube' ? (
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="youtube-url" className="form-label">YouTube Long-Form Video URL</label>
              <input
                id="youtube-url"
                type="url"
                placeholder="https://www.youtube.com/watch?v=..."
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                className="form-input"
                required
              />
              <span className="form-help">
                Authorized videos only. If the video requires authentication or is rate-limited, use the Local Video File tab.
              </span>
            </div>
          ) : (
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label htmlFor="video-file" className="form-label">Select Video File (.mp4, .mov, .mkv, .webm)</label>
              <input
                id="video-file"
                type="file"
                accept="video/mp4,video/quicktime,video/x-matroska,video/webm"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="form-input"
                required
              />
              <span className="form-help">
                Streamed directly to local persistent storage. Maximum size: 2 GB.
              </span>
            </div>
          )}
        </div>

        {/* Source Authorization Declaration */}
        <div className="card" style={{ backgroundColor: 'var(--bg-secondary)' }}>
          <label style={{ display: 'flex', alignItems: 'flex-start', gap: '0.65rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={rightsDeclared}
              onChange={(e) => setRightsDeclared(e.target.checked)}
              style={{ marginTop: '0.2rem' }}
              required
            />
            <div>
              <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                Source Rights & Permission Declaration
              </span>
              <p style={{ fontSize: '0.825rem', marginTop: '0.15rem' }}>
                I confirm that I own, hold a license for, or am authorized to process this video content. ClipForge AI does not bypass DRM or authentication.
              </p>
            </div>
          </label>
        </div>

        {/* Output Settings Card */}
        <div className="card">
          <h2 style={{ marginBottom: '1rem' }}>Clip Generation Parameters</h2>
          <div className="grid-2">
            <div className="form-group">
              <label htmlFor="aspect-ratio" className="form-label">Aspect Ratio</label>
              <select
                id="aspect-ratio"
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                className="form-select"
              >
                <option value="9:16">9:16 Vertical (Shorts, Reels, TikTok)</option>
                <option value="16:9">16:9 Landscape (Standard)</option>
                <option value="1:1">1:1 Square (Social Feed)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="subtitle-style" className="form-label">Caption Style</label>
              <select
                id="subtitle-style"
                value={subtitleStyle}
                onChange={(e) => setSubtitleStyle(e.target.value)}
                className="form-select"
              >
                <option value="hormozi_yellow">Hormozi Yellow (High Contrast Bold)</option>
                <option value="clean_white">Clean White (Minimal Sans)</option>
                <option value="minimal_box">Subtle Box (Transparent Background)</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1.5rem', marginTop: '0.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.875rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={burnSubtitles}
                onChange={(e) => setBurnSubtitles(e.target.checked)}
              />
              <span>Burn captions into video (SRT and VTT files are also generated)</span>
            </label>
          </div>
        </div>

        {/* Advanced Settings Toggle */}
        <div className="card">
          <div 
            onClick={() => setShowAdvanced(!showAdvanced)} 
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', userSelect: 'none' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
              <Settings2 size={16} />
              <span>Advanced Duration & Segment Settings</span>
            </div>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {showAdvanced ? 'Hide' : 'Show'}
            </span>
          </div>

          {showAdvanced && (
            <div style={{ marginTop: '1.25rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-color)' }}>
              <div className="grid-2">
                <div className="form-group">
                  <label htmlFor="clip-count" className="form-label">Clip Count</label>
                  <input
                    id="clip-count"
                    type="number"
                    min={1}
                    max={10}
                    value={clipCount}
                    onChange={(e) => setClipCount(Number(e.target.value))}
                    className="form-input"
                  />
                  <span className="form-help">Default: 5 distinct clips</span>
                </div>

                <div className="form-group">
                  <label htmlFor="min-duration" className="form-label">Min Duration (s)</label>
                  <input
                    id="min-duration"
                    type="number"
                    min={60}
                    value={minDuration}
                    onChange={(e) => setMinDuration(Number(e.target.value))}
                    className="form-input"
                  />
                  <span className="form-help">Hard minimum 60s enforced</span>
                </div>

                <div className="form-group">
                  <label htmlFor="target-duration" className="form-label">Target Duration (s)</label>
                  <input
                    id="target-duration"
                    type="number"
                    min={60}
                    max={120}
                    value={targetDuration}
                    onChange={(e) => setTargetDuration(Number(e.target.value))}
                    className="form-input"
                  />
                  <span className="form-help">Default: 75 seconds</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Action Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
          <button
            type="submit"
            disabled={submitting}
            className="btn btn-primary"
            style={{ padding: '0.75rem 2rem', fontSize: '1rem', fontWeight: 600 }}
          >
            <PlusCircle size={18} />
            <span>{submitting ? 'Initializing Job...' : 'Create clips'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
