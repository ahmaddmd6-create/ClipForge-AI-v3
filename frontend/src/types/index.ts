export interface SourceAsset {
  id: string;
  file_path: string;
  file_size_bytes: number;
  duration_seconds: number;
  width: number;
  height: number;
  frame_rate: number;
  video_codec: string;
  audio_codec: string;
  has_audio: boolean;
  rotation: number;
}

export interface ClipSummary {
  id: string;
  clip_index: number;
  title: string;
  hook: string;
  start_time: number;
  end_time: number;
  duration: number;
  aspect_ratio: string;
  viral_score: number;
  selection_reason: string;
  status: 'candidate' | 'rendering' | 'completed' | 'failed';
  video_path?: string;
  thumbnail_path?: string;
  file_size_mb: number;
}

export interface Job {
  id: string;
  title: string;
  source_type: 'youtube' | 'upload';
  source_url?: string;
  source_filename?: string;
  status: 'queued' | 'analyzing' | 'clipping' | 'rendering' | 'completed' | 'failed' | 'cancelled';
  stage: string;
  progress: number;
  status_message: string;
  error_detail?: string;
  target_clip_count: number;
  min_duration: number;
  target_duration: number;
  max_duration: number;
  aspect_ratio: string;
  subtitle_style: string;
  burn_subtitles: boolean;
  background_music?: string;
  rights_declared: boolean;
  detected_niche?: string;
  target_audience?: string;
  key_themes?: string;
  suitable_platforms?: string;
  confidence_score?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  source_asset?: SourceAsset;
  clips: ClipSummary[];
}

export interface ClipDetail {
  id: string;
  job_id: string;
  clip_index: number;
  title: string;
  hook: string;
  transcript_excerpt: string;
  start_time: number;
  end_time: number;
  duration: number;
  aspect_ratio: string;
  viral_score: number;
  selection_reason: string;
  status: 'candidate' | 'rendering' | 'completed' | 'failed';
  video_path?: string;
  video_url?: string;
  thumbnail_path?: string;
  thumbnail_url?: string;
  srt_url?: string;
  vtt_url?: string;
  file_size_mb: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface StorageStats {
  storage_root: string;
  outputs_directory: string;
  inputs_directory: string;
  total_used_mb: number;
  available_disk_gb: number;
  total_disk_gb: number;
  retention_days: number;
  max_concurrent_jobs: number;
  cpu_threads: number;
  transcription_provider: string;
  whisper_model: string;
  whisper_compute_type: string;
  ai_provider: string;
}
