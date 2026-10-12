import React, { useEffect, useState } from 'react';
import { RefreshCw, Folder } from 'lucide-react';
import { api } from '../api/client';
import type { StorageStats } from '../types';

export const StorageSettings: React.FC = () => {
  const [stats, setStats] = useState<StorageStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setError(null);
      const data = await api.getStorageStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load storage details.');
    }
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
            Local Windows folder persistence, CPU worker allocation, and model configuration.
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
