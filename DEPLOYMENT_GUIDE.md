# ClipForge AI - Production Live Deployment Guide

## Architecture: Vercel (Frontend) + Docker (Backend & Worker)

This is the recommended production architecture:
- **Frontend**: Hosted on **Vercel** with global edge CDN caching and zero-config SPA routing.
- **Backend & Worker**: Hosted via **Docker Compose** on your VPS, server, or cloud VM with FFmpeg, Whisper, PostgreSQL, Redis, and persistent volume storage.

```
┌──────────────────────────────────────────────┐
│        Frontend (React / Vite / SPA)         │
│          Hosted Globally on VERCEL           │
│         https://your-app.vercel.app          │
└──────────────────────┬───────────────────────┘
                       │ HTTPS API Requests (VITE_API_BASE_URL)
                       ▼
┌──────────────────────────────────────────────┐
│             Docker Backend Stack             │
│        (VPS / Cloud Host / Dedicated VM)     │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │  clipforge-api (FastAPI on Port 8005)  │  │
│  └──────────────────┬─────────────────────┘  │
│                     │ Shared DB / Queue / Disk│
│  ┌──────────────────▼─────────────────────┐  │
│  │ clipforge-worker (FFmpeg, Whisper CPU) │  │
│  └──────────────────┬─────────────────────┘  │
│                     │                        │
│   ┌─────────────────┴─────────────────┐      │
│   │ clipforge-db (PostgreSQL 15)      │      │
│   │ clipforge-redis (Redis 7 Queue)   │      │
│   │ storage/ (Persistent Render MP4s) │      │
│   └───────────────────────────────────┘      │
└──────────────────────────────────────────────┘
```

---

## Part 1: Run the Backend with Docker

### 1. Prerequisites
Ensure Docker and Docker Compose are installed on your host machine / VPS:
```bash
docker --version
docker compose version
```

### 2. Configure Environment (`.env`)
Clone the repository and copy the environment configuration:
```bash
git clone https://github.com/ahmaddmd6-create/ClipForge-AI-v3.git
cd ClipForge-AI-v3
cp .env.example .env
```
Key production variables in `.env`:
- `APP_ENV=production`
- `API_PORT=8005` (exposed host port)
- `CORS_ALLOWED_ORIGINS=https://*.vercel.app,https://your-custom-domain.com`
- `POSTGRES_PASSWORD=your_strong_postgres_password`

### 3. Launch the Complete Docker Stack
Start the FastAPI backend, background worker, PostgreSQL, and Redis:
```bash
docker compose up -d --build
```

Verify all services are healthy and running:
```bash
docker compose ps
```
You should see:
- `clipforge-api` (Port 8005 -> 8000)
- `clipforge-worker`
- `clipforge-db` (healthy)
- `clipforge-redis` (healthy)

Test backend health locally:
```bash
curl http://localhost:8005/api/health
# Returns: {"status":"healthy","service":"ClipForge AI API"}
```

---

## Part 2: Expose the Docker Backend Live

To allow your Vercel frontend to reach your Docker backend over HTTPS, choose one of the following methods:

### Option A: Free Instant Cloudflare Tunnel (Zero Port-Forwarding)
Cloudflare Tunnel gives you an instant, secure `https://` domain for your local or VPS Docker backend without configuring SSL or opening router ports:

1. Download and run `cloudflared`:
   ```bash
   cloudflared tunnel --url http://localhost:8005
   ```
2. Cloudflare will output an active HTTPS URL:
   ```text
   https://xxxx-xxxx-xxxx.trycloudflare.com
   ```
3. Use this URL as your `VITE_API_BASE_URL` on Vercel!

*(For permanent domains, you can configure a named tunnel in Cloudflare Zero Trust mapped to `api.yourdomain.com`).*

### Option B: Cloud VPS with Reverse Proxy (Nginx / Caddy + Let's Encrypt)
On an Ubuntu VPS (DigitalOcean, AWS EC2, Hetzner, Linode):
1. Point your DNS `api.yourdomain.com` (A Record) to your VPS IP address.
2. Install Caddy or Nginx:
   ```bash
   # Caddy (automatic SSL):
   # In /etc/caddy/Caddyfile:
   api.yourdomain.com {
       reverse_proxy localhost:8005
   }
   ```
3. Reload Caddy: `sudo systemctl reload caddy`.

---

## Part 3: Deploy the Frontend to Vercel

1. Go to the [Vercel Dashboard](https://vercel.com/new).
2. Connect your GitHub account and import `https://github.com/ahmaddmd6-create/ClipForge-AI-v3`.
3. Configure the project settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add the Environment Variable:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://your-backend-live-url.com` *(e.g. your Cloudflare tunnel or VPS domain)*
5. Click **Deploy**.

Vercel will build your application and provide your live frontend URL (e.g., `https://clipforge-ai-v3.vercel.app`).

---

## Part 4: Verification & Smoke Test

1. Open your live Vercel URL in your browser.
2. Verify the status badge in the header shows **"Systems Online"**.
3. Create a new job:
   - Paste a YouTube URL or upload a video file.
   - Click **Generate Clips**.
4. Monitor the processing stages:
   - `queued` → `analyzing` (Whisper transcription) → `clipping` (Niche highlight selection) → `rendering` (FFmpeg vertical 9:16 + captions) → `completed`.
5. Check your generated clips:
   - Preview with synchronized captions in the browser.
   - Click **Download MP4** or download subtitle files (SRT/VTT).
   - All files are persistently saved in `./storage/outputs/<job_id>/` on your Docker host.
