import asyncio
import glob
import os
from typing import Any
import yt_dlp

from .models import (
    DownloadOptions,
    DownloadResult,
    StreamInfo,
    SubtitleInfo,
    VideoFormat,
    VideoInfo,
)


class ProDLDownloader:

    @staticmethod
    async def get_info(url: str) -> VideoInfo:
        """
        Use yt-dlp to extract video metadata, formats, and subtitles.
        """
        opts = {
            'quiet': True,
            'no_warnings': True,
        }

        def _extract() -> VideoInfo:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise ValueError(f"Could not extract info for URL: {url}")

                # Format extraction & filtering
                raw_formats = info.get("formats") or []
                video_formats: list[VideoFormat] = []

                for fmt in raw_formats:
                    vcodec = fmt.get("vcodec")
                    acodec = fmt.get("acodec")

                    has_video = vcodec is not None and vcodec != "none"
                    has_audio = acodec is not None and acodec != "none"

                    if not (has_video or has_audio):
                        continue

                    res = fmt.get("resolution")
                    if not res:
                        w = fmt.get("width")
                        h = fmt.get("height")
                        if w and h:
                            res = f"{w}x{h}"
                        elif has_video:
                            res = "video only"
                        else:
                            res = "audio only"

                    filesize = fmt.get("filesize") or fmt.get("filesize_approx")
                    note = fmt.get("format_note") or fmt.get("note") or ""

                    video_formats.append(
                        VideoFormat(
                            format_id=str(fmt.get("format_id", "")),
                            ext=str(fmt.get("ext", "")),
                            resolution=str(res),
                            filesize=filesize,
                            note=str(note),
                            has_video=has_video,
                            has_audio=has_audio,
                        )
                    )

                # Subtitles extraction (manual + auto)
                subtitles_list: list[SubtitleInfo] = []

                raw_subs = info.get("subtitles") or {}
                for lang, lang_formats in raw_subs.items():
                    lang_name = lang
                    if isinstance(lang_formats, list) and len(lang_formats) > 0:
                        lang_name = lang_formats[0].get("name") or lang
                    subtitles_list.append(
                        SubtitleInfo(lang=str(lang), lang_name=str(lang_name), is_auto=False)
                    )

                raw_auto = info.get("automatic_captions") or {}
                for lang, lang_formats in raw_auto.items():
                    lang_name = lang
                    if isinstance(lang_formats, list) and len(lang_formats) > 0:
                        lang_name = lang_formats[0].get("name") or lang
                    subtitles_list.append(
                        SubtitleInfo(lang=str(lang), lang_name=str(lang_name), is_auto=True)
                    )

                return VideoInfo(
                    title=str(info.get("title") or ""),
                    duration=info.get("duration"),
                    thumbnail=info.get("thumbnail"),
                    uploader=info.get("uploader"),
                    view_count=info.get("view_count"),
                    webpage_url=str(info.get("webpage_url") or url),
                    extractor=str(info.get("extractor") or ""),
                    formats=video_formats,
                    subtitles=subtitles_list,
                )

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _extract)

    @staticmethod
    async def get_stream_info(opts: DownloadOptions) -> StreamInfo:
        """
        Extract direct CDN URL for video stream without downloading.
        """
        ydl_opts = {
            'quiet': True,
            'format': opts.format_id,
            'skip_download': True,
        }

        def _extract() -> StreamInfo:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(opts.url, download=False)
                if info is None:
                    raise ValueError(f"Could not extract stream info for URL: {opts.url}")

                direct_url = info.get("url")
                if not direct_url:
                    req_dl = info.get("requested_downloads")
                    if req_dl and isinstance(req_dl, list) and len(req_dl) > 0:
                        direct_url = req_dl[0].get("url")

                if not direct_url:
                    raise ValueError(f"Direct stream URL not found for: {opts.url}")

                filesize = info.get("filesize") or info.get("filesize_approx")

                return StreamInfo(
                    url=str(direct_url),
                    title=str(info.get("title") or ""),
                    ext=str(info.get("ext") or ""),
                    filesize=filesize,
                )

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _extract)

    @staticmethod
    async def download(opts: DownloadOptions) -> DownloadResult:
        """
        Download video to local disk based on options.
        """
        os.makedirs(opts.output_dir, exist_ok=True)

        ydl_opts: dict[str, Any] = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': f'{opts.output_dir}/%(id)s.%(ext)s',
            'merge_output_format': 'mp4',
        }

        if opts.audio_only:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ]
        else:
            ydl_opts['format'] = opts.format_id

        if opts.subtitles:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = opts.auto_subs
            ydl_opts['subtitleslangs'] = opts.sub_langs
            ydl_opts['embedsubtitles'] = opts.sub_embed

        if opts.thumbnail:
            ydl_opts['writethumbnail'] = True
            ydl_opts['embedthumbnail'] = opts.thumb_embed

        if opts.sponsorblock:
            if opts.sb_action == "cut":
                ydl_opts['sponsorblock_remove'] = opts.sb_categories
            elif opts.sb_action == "skip":
                ydl_opts['sponsorblock_mark'] = opts.sb_categories
            elif opts.sb_action == "mark":
                ydl_opts['sponsorblock_chapter_title'] = opts.sb_categories

        def _download() -> DownloadResult:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(opts.url, download=True)
                if info is None:
                    raise ValueError(f"Download failed for URL: {opts.url}")

                video_id = info.get("id")
                title = str(info.get("title") or "")

                # Find output file by glob pattern
                matching_files = glob.glob(f"{opts.output_dir}/{video_id}.*")

                # Exclude temporary download files or info json if any
                matching_files = [
                    f for f in matching_files
                    if not f.endswith(".part") and not f.endswith(".info.json") and not f.endswith(".ytdl")
                ]

                if matching_files:
                    filepath = matching_files[0]
                else:
                    # Fallback to requested download filename or expected filepath
                    filepath = f"{opts.output_dir}/{video_id}.mp4"

                filename = os.path.basename(filepath)
                ext = os.path.splitext(filepath)[1].lstrip(".")

                filesize = None
                if os.path.exists(filepath):
                    filesize = os.path.getsize(filepath)
                else:
                    filesize = info.get("filesize") or info.get("filesize_approx")

                return DownloadResult(
                    filepath=filepath,
                    filename=filename,
                    title=title,
                    ext=ext,
                    filesize=filesize,
                )

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _download)
