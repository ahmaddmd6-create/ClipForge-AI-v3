# ClipForge AI - Production Live Deployment Guide

This guide provides tested paths to deploy ClipForge AI live to production.

---

## Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │    Frontend (Vite / React / Tailwind)  │
                      │    Hosted on: Vercel / Cloudflare      │
                      └───────────────────┬────────────────────┘
                                          │ REST API & WebSockets
                                          ▼
                      ┌────────────────────────────────────────┐
                      │        ClipForge AI Backend API        │
                      │         (FastAPI on Port 8000)         │
                      │    Hosted on: Render / Docker / VPS    │
                      └──────────────┬─────────────┬───────────┘
                                     │             │
                    Job Dispatch     │             │ Metadata & State
                                     ▼             ▼
  ┌─────────────────────────────────────┐      ┌─────────────────────────┐
  │     ClipForge Background Worker     │      │   PostgreSQL Database   │
  │  (yt-dlp, Whisper, FFmpeg, Niche)   │      │   (Jobs, Clips, Assets) │
  └──────────────────┬──────────────────┘      └─────────────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────┐
  │      Redis 7 Persistent Queue       │
  │     (Job coordination & state)      │
  └─────────────────────────────────────┘
```

---

## Strategy A: Vercel (Frontend) + Render (Backend & Worker)

This is the recommended serverless/managed cloud combination.

### 1. Backend on Render.com
Render natively supports Python workers, managed PostgreSQL, Redis, and persistent disks using the included `render.yaml` blueprint.

1. Go to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository: `https://github.com/ahmaddmd6-create/ClipForge-AI-v3`.
4. Render will detect `render.yaml` and configure:
   - `clipforge-api`: FastAPI Web Service.
   - `clipforge-worker`: Background worker with FFmpeg and Whisper.
   - `clipforge-db`: Managed PostgreSQL database.
   - `clipforge-redis`: Managed Redis instance.
5. In the Render Dashboard, set your environment variables:
   - `OPENAI_API_KEY`: *(Optional)* If using OpenAI GPT-4o / Whisper API.
   - `ANTHROPIC_API_KEY`: *(Optional)* If using Claude for niche analysis.
6. Click **Apply**. Once deployed, copy your API URL (e.g., `https://clipforge-api.onrender.com`).

### 2. Frontend on Vercel
1. Go to [Vercel Dashboard](https://vercel.com/new).
2. Import the GitHub repository: `ClipForge-AI`.
3. Set the **Root Directory** to `frontend`.
4. Add the Environment Variable:
   - `VITE_API_BASE_URL`: `https://clipforge-api.onrender.com/api`
5. Click **Deploy**. Vercel will build and publish your SPA globally with CDN edge caching.

---

## Strategy B: Cloudflare Pages (Frontend) + Docker (Backend via Cloudflare Tunnel)

Ideal for cost-free frontend edge hosting and hosting your compute-heavy video rendering on your own server or GPU VPS.

### 1. Frontend on Cloudflare Pages
1. Go to the [Cloudflare Dashboard](https://dash.cloudflare.com) → **Workers & Pages** → **Create application** → **Pages**.
2. Connect your GitHub repo (`ClipForge-AI`).
3. Build Settings:
   - **Root directory**: `frontend`
   - **Framework preset**: `Vite`
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
4. Environment Variables:
   - `VITE_API_BASE_URL`: `https://api.yourdomain.com/api` (or your Cloudflare Tunnel URL).
5. Click **Save and Deploy**.

### 2. Backend & Worker via Docker + Cloudflare Tunnel
1. On your VPS or host machine, clone the repository:
   ```bash
   git clone https://github.com/ahmaddmd6-create/ClipForge-AI-v3.git
   cd ClipForge-AI
   cp .env.example .env
   ```
2. Launch the full production stack:
   ```bash
   docker compose up -d --build
   ```
3. Expose the API publicly through Cloudflare Tunnel (no port forwarding or public IP required):
   ```bash
   # Install cloudflared
   cloudflared tunnel --url http://localhost:8080
   ```
4. Copy the generated `https://xxxx.trycloudflare.com` URL and set it as `VITE_API_BASE_URL` on Cloudflare Pages.

---

## Strategy C: Complete Single-Host Docker Deployment

For self-hosting on AWS EC2, DigitalOcean Droplet, Hetzner, or Linode:

```bash
git clone https://github.com/ahmaddmd6-create/ClipForge-AI-v3.git
cd ClipForge-AI
cp .env.example .env
docker compose up -d
```
All services (Frontend Nginx on port 8080, FastAPI on port 8000, Worker, PostgreSQL, Redis) start automatically with health checks and restart policies.
