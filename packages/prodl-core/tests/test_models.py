import pytest
from prodl_core.models import (
    VideoFormat,
    SubtitleInfo,
    VideoInfo,
    DownloadOptions,
    DownloadResult,
    StreamInfo,
)


def test_models_instantiation():
    fmt = VideoFormat(
        format_id="137",
        ext="mp4",
        resolution="1080p",
        filesize=1000,
        note="1080p",
        has_video=True,
        has_audio=False,
    )
    assert fmt.format_id == "137"

    sub = SubtitleInfo(lang="en", lang_name="English", is_auto=False)
    assert sub.is_auto is False

    info = VideoInfo(
        title="Test Video",
        duration=120,
        thumbnail="https://example.com/thumb.jpg",
        uploader="Test User",
        view_count=500,
        webpage_url="https://example.com/watch?v=123",
        extractor="youtube",
        formats=[fmt],
        subtitles=[sub],
    )
    assert info.title == "Test Video"

    opts = DownloadOptions(url="https://example.com/watch?v=123")
    assert opts.sub_langs == ["en", "ar"]
    assert opts.sb_action == "cut"

    res = DownloadResult(
        filepath="/tmp/prodl_downloads/123.mp4",
        filename="123.mp4",
        title="Test Video",
        ext="mp4",
        filesize=1000,
    )
    assert res.ext == "mp4"

    stream = StreamInfo(
        url="https://cdn.example.com/stream.mp4",
        title="Test Stream",
        ext="mp4",
        filesize=1000,
    )
    assert stream.url == "https://cdn.example.com/stream.mp4"
