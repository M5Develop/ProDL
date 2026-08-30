import asyncio
import json
import yt_dlp
from .models import SubtitleInfo


async def list_subtitles(url: str) -> list[SubtitleInfo]:
    """
    Use yt-dlp to list available subtitles.
    Options: {'listsubtitles': True, 'quiet': True}
    Parse info['subtitles'] → is_auto: False
    Parse info['automatic_captions'] → is_auto: True
    Return list[SubtitleInfo]
    """
    opts = {
        'listsubtitles': True,
        'quiet': True,
    }

    def _extract() -> list[SubtitleInfo]:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return []

            subtitles_list: list[SubtitleInfo] = []

            # Manual subtitles
            raw_subs = info.get("subtitles") or {}
            for lang, lang_formats in raw_subs.items():
                lang_name = lang
                if isinstance(lang_formats, list) and len(lang_formats) > 0:
                    lang_name = lang_formats[0].get("name") or lang
                subtitles_list.append(
                    SubtitleInfo(lang=lang, lang_name=str(lang_name), is_auto=False)
                )

            # Auto-generated subtitles
            raw_auto = info.get("automatic_captions") or {}
            for lang, lang_formats in raw_auto.items():
                lang_name = lang
                if isinstance(lang_formats, list) and len(lang_formats) > 0:
                    lang_name = lang_formats[0].get("name") or lang
                subtitles_list.append(
                    SubtitleInfo(lang=lang, lang_name=str(lang_name), is_auto=True)
                )

            return subtitles_list

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _extract)
