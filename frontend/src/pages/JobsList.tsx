import React, { useEffect, useState } from 'react';
import { RefreshCw, Eye, Trash2, PlusCircle } from 'lucide-react';
import { api } from '../api/client';
import type { Job } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ProgressBar } from '../components/ProgressBar';
import { ConfirmModal } from '../components/ConfirmModal';

interface JobsListProps {
  onNavigate: (tab: string, jobId?: string) => void;
}

export const JobsList: React.FC<JobsListProps> = ({ onNavigate }) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);

  const fetchJobs = async () => {
    try {
      setError(null);
      const data = await api.getJobs(filterStatus === 'all' ? undefined : filterStatus);
      setJobs(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch jobs.');
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 4000);
    return () => clearInterval(interval);
  }, [filterStatus]);

  const handleDelete = async () => {
    if (!deleteTargetId) return;
    try {
      await api.deleteJob(deleteTargetId);
      setDeleteTargetId(null);
      fetchJobs();
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleRetry = async (jobId: string) => {
    try {
      await api.retryJob(jobId);
      fetchJobs();
    } catch (err: any) {
      alert(`Retry failed: ${err.message}`);
    }
  };

  const filteredJobs = jobs.filter((j) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return j.title.toLowerCase().includes(q) || j.id.toLowerCase().includes(q) || (j.detected_niche || '').toLowerCase().includes(q);
  });

  return (
    <div className="container" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>Jobs Management</h1>
          <p style={{ marginTop: '0.25rem' }}>Monitor, retry, and inspect all active and completed clipping jobs.</p>
        </div>
        <button onClick={() => onNavigate('create')} className="btn btn-primary">
          <PlusCircle size={16} />
          <span>Create clips</span>
        </button>
      </div>

      {error && (
        <div className="card" style={{ backgroundColor: 'var(--status-danger-bg)', color: 'var(--status-danger)' }}>
          {error}
        </div>
      )}

      {/* Filters & Search */}
      <div className="card" style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {['all', 'queued', 'rendering', 'completed', 'failed'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`btn ${filterStatus === st ? 'btn-primary' : 'btn-secondary'}`}
              style={{ textTransform: 'capitalize', padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
            >
              {st}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search by title or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="form-input"
              style={{ padding: '0.35rem 0.75rem', width: '220px', fontSize: '0.85rem' }}
            />
          </div>
          <button onClick={fetchJobs} className="btn btn-secondary" style={{ padding: '0.35rem 0.65rem' }}>
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0 }}>
        {filteredJobs.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            No jobs match the selected filter.
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
                {filteredJobs.map((job) => (
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
                      <div style={{ display: 'inline-flex', gap: '0.35rem' }}>
                        <button
                          onClick={() => onNavigate('workspace', job.id)}
                          className="btn btn-secondary"
                          style={{ padding: '0.35rem 0.6rem', fontSize: '0.8rem' }}
                        >
                          <Eye size={13} />
                          <span>View</span>
                        </button>
                        {job.status === 'failed' && (
                          <button
                            onClick={() => handleRetry(job.id)}
                            className="btn btn-secondary"
                            style={{ padding: '0.35rem 0.6rem', fontSize: '0.8rem' }}
                          >
                            <RefreshCw size={13} />
                            <span>Retry</span>
                          </button>
                        )}
                        <button
                          onClick={() => setDeleteTargetId(job.id)}
                          className="btn btn-secondary"
                          style={{ padding: '0.35rem 0.6rem', fontSize: '0.8rem', color: 'var(--status-danger)' }}
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
        title="Delete Job"
        message="Are you sure you want to delete this job and all its rendered video clips?"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTargetId(null)}
      />
    </div>
  );
};
