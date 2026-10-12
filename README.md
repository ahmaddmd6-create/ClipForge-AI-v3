# ClipForge AI — Autonomous Video Clipping Workstation

ClipForge AI is a production-grade, local-first application that converts long-form YouTube videos and local video uploads into high-engagement **60–90 second vertical short-form clips** (TikTok, YouTube Shorts, Instagram Reels) with AI highlight detection, burned-in subtitles, and persistent local storage on Windows.

---

## 1. System Architecture

```
flowchart TD
    A[Paste YouTube URL or Upload Video] --> B[Validate Source and Permissions]
    B --> C[Inspect Media with FFprobe]
    C --> D[Transcribe Audio via faster-whisper CPU INT8]
    D --> E[Detect Niche & Extract Candidate Moments]
    E --> F[Rank and Validate 5 Distinct Clips >= 60s]
    F --> G[Reframe to 9:16 & Generate ASS/SRT/VTT Captions]
    G --> H[Render with FFmpeg on CPU]
    H --> I[Verify Each Output is >= 60s with FFprobe]
    I --> J[Save MP4 & manifest.json to Windows Storage Folder]
    J --> K[Preview, Download and Manage Clips in Web UI]
```

### Directory Structure

```
gainearn/
├── frontend/
│   ├── src/
│   │   ├── api/client.ts          # Typed Fetch API client
│   │   ├── components/            # Navbar, Footer, ProgressBar, StatusBadge, ConfirmModal
│   │   ├── pages/                 # Dashboard, CreateJob, AnalysisWorkspace, JobsList,
│   │   │                          # ClipLibrary, ClipDetail, StorageSettings, Legal pages
│   │   ├── types/index.ts         # TypeScript models
│   │   ├── App.tsx                # Routing and main application container
│   │   └── main.tsx               # Entry point
│   ├── Dockerfile                 # Multi-stage Node + Nginx build
│   ├── nginx.conf                 # Nginx reverse proxy with 2GB upload limit
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/routes/            # jobs, clips, storage, health routes
│   │   ├── core/                  # config, security (SSRF & path traversal), events
│   │   ├── db/                    # SQLAlchemy engine & session (Postgres & SQLite fallback)
│   │   ├── models/                # Job, SourceAsset, Clip, TranscriptSegment, RenderingAttempt
│   │   ├── schemas/               # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── media/             # FFprobe inspector, YouTube downloader, chunked uploader
│   │   │   ├── transcription/     # faster-whisper CPU INT8 speech recognition
│   │   │   ├── niche_detection/   # Content topic & audience hypothesis analyzer
│   │   │   ├── clip_selection/    # 5-clip selection enforcing >= 60s duration
│   │   │   ├── rendering/         # FFmpeg 9:16 reframe, ASS/SRT/VTT generator, MP4 encoder
│   │   │   └── storage/           # manifest.json generator, disk metrics
│   │   ├── workers/queue.py       # Redis-backed task queue with in-process fallback
│   │   ├── main.py                # FastAPI web service
│   │   └── worker.py              # Asynchronous background video worker
│   ├── tests/                     # Unit and media integration tests
│   ├── requirements.txt           # Pinned Python dependencies
│   └── Dockerfile                 # Python 3.12 + FFmpeg Debian container
├── storage/
│   ├── inputs/                    # Uploaded & downloaded source video files
│   ├── outputs/                   # Rendered MP4 clips, subtitles, and manifest.json
│   ├── models/                    # Cached Whisper model weights
│   ├── thumbnails/                # Generated video thumbnail images
│   └── temporary/                 # Intermediate rendering artifacts
├── docker-compose.yml             # 5-service stack: frontend, api, worker, redis, postgres
├── .env.example                   # Environment variable template
├── README.md                      # Documentation
└── SECURITY.md                    # Security policy
```

---

## 2. Quick Start on Windows with Docker

### Prerequisites
- Windows 10 or 11 with **Docker Desktop** (WSL 2 backend enabled).
- At least 8 GB of RAM and 10 GB of free disk space.

### PowerShell Startup Commands

```powershell
# 1. Clone or open the project folder
cd C:\Users\Ghosty\Desktop\gainearn

# 2. Create the local storage directories
New-Item -ItemType Directory -Force -Path `
  storage/inputs, `
  storage/outputs, `
  storage/models, `
  storage/thumbnails, `
  storage/temporary

# 3. Create your local environment file
Copy-Item .env.example .env

# 4. Validate Docker Compose configuration
docker compose config --quiet

# 5. Build and start all services in the background
docker compose up --build -d

# 6. Check container health status
docker compose ps

# 7. Open the application in your browser
Start-Process "http://localhost:8080"
```

---

## 3. Where Generated Clips Are Saved on Windows

All rendered videos are stored directly on your Windows host machine under:
```
C:\Users\Ghosty\Desktop\gainearn\storage\outputs\<job_id>\
```

Each job folder contains:
- `clip_01.mp4` through `clip_05.mp4` (all guaranteed >= 60 seconds)
- `clip_01.srt` and `clip_01.vtt` subtitle files
- `clip_01.jpg` thumbnail image
- `manifest.json` (complete metadata manifest with timestamps, durations, and topics)

---

## 4. CPU-Only Optimization Settings

ClipForge AI is pre-configured for smooth execution on standard multi-core CPUs:

| Setting | Value | Rationale |
| :--- | :--- | :--- |
| `MAX_CONCURRENT_JOBS` | `1` | Prevents CPU starvation during intensive video rendering |
| `CPU_THREADS` | `2` | Allocates predictable compute threads for transcription |
| `WHISPER_MODEL` | `small` | Balanced accuracy and speed on CPU |
| `WHISPER_COMPUTE_TYPE` | `int8` | 4x faster quantization without GPU |
| `MIN_CLIP_DURATION_SECONDS` | `60.0` | Mandatory hard minimum duration enforced in backend |
| `TARGET_CLIP_DURATION_SECONDS` | `75.0` | Ideal short-form duration (60–90 seconds) |

---

## 5. Running Automated Tests Locally

You can run the full test suite (including synthetic media generation and duration validation):

```powershell
# Run backend tests
python -m pytest backend/tests -v
```

---

## 6. Common Operations & Troubleshooting

### Viewing Logs
```powershell
docker compose logs --tail 100 -f api worker frontend
```

### Stopping Services (Preserving Rendered Videos and Database)
```powershell
docker compose down
```

### Resetting Stuck Jobs
If the host computer was shut down or restarted while a job was rendering, the worker automatically recovers stale jobs on startup and marks them as retryable. Click **Retry** on the Dashboard or Jobs page.
