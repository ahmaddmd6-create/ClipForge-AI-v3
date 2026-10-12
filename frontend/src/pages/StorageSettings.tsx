import React, { useEffect, useState } from 'react';
import { RefreshCw, Folder, Globe, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';
import type { StorageStats } from '../types';

export const StorageSettings: React.FC = () => {
  const [stats, setStats] = useState<StorageStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendUrl, setBackendUrl] = useState<string>(() => api.getStoredBackendUrl());
  const [saveSuccess, setSaveSuccess] = useState(false);

  const fetchStats = async () => {
    try {
      setError(null);
      const data = await api.getStorageStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load storage details.');
    }
  };

  const handleSaveBackend = async () => {
    api.setStoredBackendUrl(backendUrl);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
    fetchStats();
  };

  const handleResetBackend = async () => {
    api.setStoredBackendUrl('');
    setBackendUrl('');
    fetchStats();
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '820px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Storage & System Settings</h1>
          <p style={{ marginTop: '0.25rem' }}>
            Local Windows folder persistence, live backend connection, and model configuration.
          </p>
        </div>
        <button onClick={fetchStats} className="btn btn-secondary">
          <RefreshCw size={14} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="card" style={{ backgroundColor: 'var(--status-danger-bg)', color: 'var(--status-danger)' }}>
          {error}
        </div>
      )}

      {/* Backend API Connection */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <Globe size={18} />
          <h2>Backend API Connection</h2>
        </div>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
          Configure the live API endpoint for this Vercel deployment. Connect to your Docker backend via Cloudflare Tunnel or your VPS.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Active Endpoint
            </label>
            <code style={{ display: 'block', padding: '0.5rem 0.75rem', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem' }}>
              {api.getApiBase()}
            </code>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Custom Backend URL (e.g., https://xxxx.trycloudflare.com or https://api.yourdomain.com)
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <input
                type="text"
                value={backendUrl}
                onChange={(e) => setBackendUrl(e.target.value)}
                placeholder="https://xxxx.trycloudflare.com"
                style={{
                  flex: 1,
                  minWidth: '260px',
                  padding: '0.5rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                  fontSize: '0.875rem',
                  backgroundColor: 'var(--bg-primary)',
                  color: 'var(--text-primary)'
                }}
              />
              <button onClick={handleSaveBackend} className="btn btn-primary">
                Save & Connect
              </button>
              {backendUrl && (
                <button onClick={handleResetBackend} className="btn btn-secondary">
                  Reset
                </button>
              )}
            </div>
            {saveSuccess && (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: 'var(--status-success)', fontSize: '0.8rem', marginTop: '0.35rem' }}>
                <CheckCircle2 size={14} /> Backend URL saved! Reconnecting...
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Windows Folder Access Instructions */}
      <div className="card" style={{ backgroundColor: 'var(--bg-secondary)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <Folder size={18} />
          <h2>Local Windows File Access</h2>
        </div>
        <p style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>
          All completed jobs and clips are saved directly onto your host computer in the repository storage directory. You can open them in Windows File Explorer anytime:
        </p>
        <code style={{ display: 'block', padding: '0.65rem 0.85rem', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem' }}>
          {stats ? `${stats.outputs_directory}` : 'storage\\outputs\\<job_id>\\'}
        </code>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          Inside each job folder: <strong>clip_01.mp4</strong> to <strong>clip_05.mp4</strong>, subtitles (<strong>.srt</strong>, <strong>.vtt</strong>), thumbnails, and <strong>manifest.json</strong>.
        </p>
      </div>

      {/* Disk Usage Overview */}
      <div className="card">
        <h2>Disk Consumption</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', marginTop: '1rem', fontSize: '0.875rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Total Storage Used by ClipForge</span>
            <strong>{stats ? `${stats.total_used_mb} MB` : 'Calculating...'}</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Available Disk Space on Host Drive</span>
            <strong>{stats ? `${stats.available_disk_gb} GB free` : 'Checking...'}</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Automatic Output Retention</span>
            <span>{stats ? `${stats.retention_days} days` : '30 days'}</span>
          </div>
        </div>
      </div>

      {/* Worker & Model Diagnostics */}
      <div className="card">
        <h2>CPU & AI Model Diagnostics</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', marginTop: '1rem', fontSize: '0.875rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Active Transcription Provider</span>
            <strong>{stats?.transcription_provider || 'faster-whisper'}</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Whisper Model & Compute Type</span>
            <strong>{stats ? `${stats.whisper_model} (${stats.whisper_compute_type})` : 'small (int8)'}</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Worker CPU Thread Allocation</span>
            <strong>{stats?.cpu_threads || 2} threads</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Maximum Concurrent Jobs</span>
            <span>{stats?.max_concurrent_jobs || 1} job at a time (CPU protected)</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>AI Niche Analyzer</span>
            <span>Deterministic Local Baseline & Heuristic Ranking</span>
          </div>
        </div>
      </div>
    </div>
  );
};
