from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp, os, uuid, asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(title="ProDL API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=3)
DOWNLOAD_DIR = "/tmp/prodl_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── Models ───────────────────────────────────────────────────────────────────

class InfoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    audio_only: bool = False

# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_info(url: str):
    with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
        return ydl.extract_info(url, download=False)

def _download(url: str, format_id: str, audio_only: bool):
    uid = str(uuid.uuid4())[:8]
    if audio_only:
        fmt = 'bestaudio/best'
        postprocessors = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        ext = 'mp3'
    else:
        fmt = format_id
        postprocessors = []
        ext = 'mp4'

    ydl_opts = {
        'format': fmt,
        'outtmpl': f'{DOWNLOAD_DIR}/{uid}.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': postprocessors,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return f'{DOWNLOAD_DIR}/{uid}.{ext}', info.get('title', 'video')

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "ProDL API 🚀", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/info")
async def get_info(req: InfoRequest):
    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(executor, _get_info, req.url)
        formats = []
        for f in info.get('formats', []):
            has_video = f.get('vcodec', 'none') != 'none'
            has_audio = f.get('acodec', 'none') != 'none'
            if not (has_video or has_audio):
                continue
            formats.append({
                'format_id':  f.get('format_id'),
                'ext':        f.get('ext'),
                'resolution': f.get('resolution', 'audio only'),
                'filesize':   f.get('filesize'),
                'note':       f.get('format_note', ''),
                'has_video':  has_video,
                'has_audio':  has_audio,
            })
        return {
            'title':      info.get('title'),
            'duration':   info.get('duration'),
            'thumbnail':  info.get('thumbnail'),
            'uploader':   info.get('uploader'),
            'view_count': info.get('view_count'),
            'webpage_url':info.get('webpage_url'),
            'extractor':  info.get('extractor'),
            'formats':    formats,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/download")
async def download(req: DownloadRequest):
    try:
        loop = asyncio.get_event_loop()
        filename, title = await loop.run_in_executor(
            executor, _download, req.url, req.format_id, req.audio_only
        )
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")[:60].strip()
        ext = 'mp3' if req.audio_only else 'mp4'
        return FileResponse(
            path=filename,
            filename=f"{safe_title}.{ext}",
            media_type='application/octet-stream',
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
