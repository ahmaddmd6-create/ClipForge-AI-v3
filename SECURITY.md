# Security Policy — ClipForge AI

## 1. Security Architecture & Threat Model

ClipForge AI treats all URLs, filenames, uploaded files, transcripts, and model outputs as untrusted input.

### SSRF Protection
- All input YouTube URLs are strictly validated against an explicit whitelist of YouTube domains (`youtube.com`, `www.youtube.com`, `m.youtube.com`, `youtu.be`).
- Hostnames are resolved before connection and checked against private, loopback, link-local, and reserved IP ranges (RFC 1918 / RFC 3927 / RFC 4291).
- Non-HTTP/HTTPS schemes (such as `file://`, `gopher://`, `dict://`) are rejected.

### Subprocess Execution Safety
- All FFmpeg and FFprobe invocations use list-based arguments without shell string interpolation (`shell=False`).
- Execution timeouts and strict error code checking are enforced.

### Path Traversal Defense
- File paths are validated with `safe_join()`.
- Filenames are sanitized and mapped to unique internal job identifiers (`job_<date>_<hex>`).
- Direct user-controlled directory navigation is blocked.

### File Upload Protection
- Allowed file extensions are limited to standard video containers (`.mp4`, `.mov`, `.mkv`, `.webm`, `.avi`).
- Magic byte signatures are inspected.
- Maximum upload size is enforced during streaming chunk ingestion (default 2048 MB).

### Isolated Docker Network
- PostgreSQL and Redis do not publish host ports. They communicate exclusively over the internal bridge network created by Docker Compose.
- Only the frontend reverse proxy port (`127.0.0.1:8080`) is exposed locally.

## 2. Reporting a Vulnerability

If you identify a security vulnerability in ClipForge AI, please report it privately:
- Email: `security@clipforge.local`
- We aim to acknowledge receipt within 48 hours and provide a patch promptly.
