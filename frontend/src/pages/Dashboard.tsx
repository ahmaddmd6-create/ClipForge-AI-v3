import React, { useEffect, useState } from 'react';
import { PlusCircle, Film, RefreshCw, AlertCircle, Eye, Trash2 } from 'lucide-react';
import { api } from '../api/client';
import type { Job, StorageStats } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ProgressBar } from '../components/ProgressBar';
import { ConfirmModal } from '../components/ConfirmModal';

interface DashboardProps {
  onNavigate: (tab: string, jobId?: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [storage, setStorage] = useState<StorageStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setError(null);
      const [jobsData, storageData] = await Promise.all([
        api.getJobs(),
        api.getStorageStats().catch(() => null),
      ]);
      setJobs(jobsData);
      setStorage(storageData);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend service.');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleDeleteJob = async () => {
    if (!deleteTargetId) return;
    try {
      await api.deleteJob(deleteTargetId);
      setDeleteTargetId(null);
      fetchData();
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleRetryJob = async (jobId: string) => {
    try {
      await api.retryJob(jobId);
      fetchData();
    } catch (err: any) {
      alert(`Retry failed: ${err.message}`);
    }
  };

  const completedClipsCount = jobs.reduce((sum, j) => sum + (j.clips?.length || 0), 0);
  const activeJobsCount = jobs.filter((j) => ['queued', 'analyzing', 'clipping', 'rendering'].includes(j.status)).length;

  return (
    <div className="container" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner */}
      <div 
        className="card"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          backgroundColor: 'var(--bg-secondary)'
        }}
      >
        <div>
          <h1>Autonomous Video Clipping Workstation</h1>
          <p style={{ marginTop: '0.25rem' }}>
            Transform long YouTube videos and local uploads into 60s+ vertical clips with AI highlight analysis and subtitles.
          </p>
        </div>
        <button 
          onClick={() => onNavigate('create')}
          className="btn btn-primary"
          style={{ padding: '0.65rem 1.25rem', fontSize: '0.95rem' }}
        >
          <PlusCircle size={17} />
          <span>Create clips</span>
        </button>
      </div>

      {error && (
        <div className="card" style={{ backgroundColor: 'var(--status-danger-bg)', borderColor: '#fecaca', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-danger)' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid-3">
        <div className="card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Active Jobs</span>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.35rem' }}>
            {activeJobsCount}
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Processing on CPU</span>
        </div>

        <div className="card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Completed Clips</span>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.35rem' }}>
            {completedClipsCount}
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Minimum 60s per clip</span>
        </div>

        <div className="card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Local Storage</span>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.35rem' }}>
            {storage ? `${storage.total_used_mb} MB` : 'Checking...'}
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            {storage ? `${storage.available_disk_gb} GB disk available` : 'Saved in storage/outputs'}
          </span>
        </div>
      </div>

      {/* Recent Jobs Section */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Recent Jobs</h2>
          <button onClick={fetchData} className="btn btn-secondary" style={{ padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}>
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
        </div>

        {jobs.length === 0 ? (
          <div style={{ padding: '3rem 1.5rem', textAlign: 'center' }}>
            <Film size={32} style={{ color: 'var(--text-muted)', margin: '0 auto 0.75rem' }} />
            <h3>No clipping jobs yet</h3>
            <p style={{ marginTop: '0.25rem', marginBottom: '1rem' }}>
              Paste a YouTube link or upload a local video file to generate your first five vertical clips.
            </p>
            <button onClick={() => onNavigate('create')} className="btn btn-primary">
              <PlusCircle size={15} />
              <span>Create clips</span>
            </button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Job Title / ID</th>
                  <th>Source</th>
                  <th>Niche</th>
                  <th>Status & Progress</th>
                  <th>Clips</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs.slice(0, 10).map((job) => (
                  <tr key={job.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{job.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{job.id}</div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.85rem' }}>{job.source_type === 'youtube' ? 'YouTube' : 'Upload'}</span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.85rem' }}>{job.detected_niche || 'Analyzing...'}</span>
                    </td>
                    <td style={{ minWidth: '180px' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                        <StatusBadge status={job.status} />
                        {['queued', 'analyzing', 'clipping', 'rendering'].includes(job.status) && (
                          <ProgressBar progress={job.progress} statusMessage={job.status_message} />
                        )}
                        {job.status === 'failed' && job.error_detail && (
                          <div style={{ fontSize: '0.75rem', color: 'var(--status-danger)' }}>{job.error_detail}</div>
                        )}
                      </div>
                    </td>
                    <td>
                      <span style={{ fontWeight: 600 }}>{job.clips?.length || 0}</span> / {job.target_clip_count}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.4rem' }}>
                        <button 
                          onClick={() => onNavigate('workspace', job.id)} 
                          className="btn btn-secondary"
                          style={{ padding: '0.35rem 0.6rem', fontSize: '0.8rem' }}
                          title="View Analysis Workspace"
                        >
                          <Eye size={13} />
                          <span>View</span>
                        </button>

                        {job.status === 'failed' && (
                          <button 
                            onClick={() => handleRetryJob(job.id)}
                            className="btn btn-secondary"
                            style={{ padding: '0.35rem 0.6rem', fontSize: '0.8rem' }}
                            title="Retry Job"
                          >
                            <RefreshCw size={13} />
                            <span>Retry</span>
                          </button>
                        )}

                        <button 
                          onClick={() => setDeleteTargetId(job.id)}
                          className="btn btn-secondary"
                          style={{ padding: '0.35rem 0.6rem', fontSize: '0.8rem', color: 'var(--status-danger)' }}
                          title="Delete Job"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ConfirmModal
        isOpen={Boolean(deleteTargetId)}
        title="Delete Clipping Job"
        message="Are you sure you want to delete this job? All associated rendered MP4 files and transcripts in storage/outputs will be permanently deleted."
        onConfirm={handleDeleteJob}
        onCancel={() => setDeleteTargetId(null)}
      />
    </div>
  );
};
