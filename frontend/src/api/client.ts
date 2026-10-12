import type { Job, ClipDetail, StorageStats } from '../types';

// In production (Vercel), VITE_API_BASE_URL points to your Render backend.
// In local dev, empty string uses Vite's proxy (/api → localhost:8005).
const BACKEND = (import.meta.env.VITE_API_BASE_URL as string) || '';
const API_BASE = `${BACKEND}/api`;

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (data.detail) {
        errorDetail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // Use fallback errorDetail
    }
    throw new Error(errorDetail);
  }
  if (res.status === 204) {
    return {} as T;
  }
  return res.json();
}

export const api = {
  async getHealth(): Promise<{ status: string; service: string }> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  async getStorageStats(): Promise<StorageStats> {
    const res = await fetch(`${API_BASE}/storage`);
    return handleResponse<StorageStats>(res);
  },

  async createJob(formData: FormData): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<Job>(res);
  },

  async getJobs(status?: string): Promise<Job[]> {
    const url = status ? `${API_BASE}/jobs?status=${encodeURIComponent(status)}` : `${API_BASE}/jobs`;
    const res = await fetch(url);
    return handleResponse<Job[]>(res);
  },

  async getJob(jobId: string): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs/${encodeURIComponent(jobId)}`);
    return handleResponse<Job>(res);
  },

  async retryJob(jobId: string): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs/${encodeURIComponent(jobId)}/retry`, {
      method: 'POST',
    });
    return handleResponse<Job>(res);
  },

  async cancelJob(jobId: string): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs/${encodeURIComponent(jobId)}/cancel`, {
      method: 'POST',
    });
    return handleResponse<Job>(res);
  },

  async deleteJob(jobId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/jobs/${encodeURIComponent(jobId)}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(res);
  },

  async getClips(jobId?: string, status?: string): Promise<ClipDetail[]> {
    const params = new URLSearchParams();
    if (jobId) params.append('job_id', jobId);
    if (status) params.append('status', status);
    const url = `${API_BASE}/clips?${params.toString()}`;
    const res = await fetch(url);
    return handleResponse<ClipDetail[]>(res);
  },

  async getClip(clipId: string): Promise<ClipDetail> {
    const res = await fetch(`${API_BASE}/clips/${encodeURIComponent(clipId)}`);
    return handleResponse<ClipDetail>(res);
  },

  async updateClip(clipId: string, updates: { title?: string; start_time?: number; end_time?: number; aspect_ratio?: string }): Promise<ClipDetail> {
    const res = await fetch(`${API_BASE}/clips/${encodeURIComponent(clipId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return handleResponse<ClipDetail>(res);
  },

  async deleteClip(clipId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/clips/${encodeURIComponent(clipId)}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(res);
  },
};
