<div align="center">
  <h1>ProDL 🚀</h1>
  <p>Free, open-source video & audio downloader. Supports YouTube, Twitter, TikTok, and 1000+ sites.</p>
  <p>
    <img src="https://img.shields.io/badge/license-AGPL--v3-blue" />
    <img src="https://img.shields.io/badge/python-3.12-green" />
    <img src="https://img.shields.io/badge/powered%20by-yt--dlp-red" />
  </p>
</div>

---

## Features

- ✅ Download from 1000+ sites (YouTube, Twitter, TikTok, Instagram, and more)
- ✅ Choose video quality (144p → 4K)
- ✅ Audio-only MP3 extraction
- ✅ Clean dark UI, no ads, no tracking
- ✅ Self-hostable with Docker
- ✅ REST API for developers

## Quick Start (Docker)

```bash
git clone https://github.com/M5Develop/ProDL
cd ProDL
docker-compose up -d
```

Then open `http://localhost:3000`

## API Usage

```bash
# Get video info
curl -X POST http://localhost:8000/info \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=..."}'

# Download video
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "...", "format_id": "137+140", "audio_only": false}' \
  --output video.mp4
```

## Deploy Options

| Platform | Cost | Notes |
|----------|------|-------|
| Self-hosted (Docker) | Free | Full control |
| Hugging Face Spaces | Free | Docker support |
| Koyeb | Free tier | Easy deploy |

## License

GNU Affero General Public License v3.0 — see [LICENSE](LICENSE)
