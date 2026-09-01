from typing import Callable, Literal
from pydantic import BaseModel


class VideoFormat(BaseModel):
    format_id: str
    ext: str
    resolution: str
    filesize: int | None
    note: str
    has_video: bool
    has_audio: bool


class SubtitleInfo(BaseModel):
    lang: str
    lang_name: str
    is_auto: bool  # YouTube auto-generated


class VideoInfo(BaseModel):
    title: str
    duration: int | None
    thumbnail: str | None
    uploader: str | None
    view_count: int | None
    webpage_url: str
    extractor: str
    formats: list[VideoFormat]
    subtitles: list[SubtitleInfo]  # available subs


class DownloadOptions(BaseModel):
    """
    Options for downloading media.

    progress_hook signature called by yt-dlp:
        def hook(d: dict):
            d['status']        # 'downloading' | 'finished' | 'error'
            d['_percent_str']  # '45.2%'
            d['_speed_str']    # '1.23MiB/s'
            d['eta']           # seconds remaining (int)
    """
    url: str
    format_id: str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
    audio_only: bool = False

    # Subtitles
    subtitles: bool = False
    sub_langs: list[str] = ["en", "ar"]
    sub_embed: bool = False
    auto_subs: bool = True

    # Thumbnail
    thumbnail: bool = False
    thumb_embed: bool = True  # embed in MP3 as cover art

    # SponsorBlock
    sponsorblock: bool = False
    sb_action: Literal["skip", "cut", "mark"] = "cut"
    sb_categories: list[str] = ["sponsor", "intro", "outro"]

    # Output
    output_dir: str = "/tmp/prodl_downloads"

    progress_hook: Callable | None = None
    max_filesize: str | None = None

    class Config:
        arbitrary_types_allowed = True


class DownloadResult(BaseModel):
    filepath: str
    filename: str
    title: str
    ext: str
    filesize: int | None


class StreamInfo(BaseModel):
    url: str  # direct stream URL from yt-dlp
    title: str
    ext: str
    filesize: int | None
