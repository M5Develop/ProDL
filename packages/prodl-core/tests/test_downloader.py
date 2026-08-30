import pytest
from unittest.mock import MagicMock, patch
from prodl_core.downloader import ProDLDownloader
from prodl_core.models import DownloadOptions, DownloadResult, StreamInfo, VideoInfo


@pytest.mark.asyncio
async def test_get_info_mock():
    mock_info = {
        "title": "Mock Title",
        "duration": 60,
        "thumbnail": "https://example.com/thumb.jpg",
        "uploader": "Uploader",
        "view_count": 100,
        "webpage_url": "https://example.com/video",
        "extractor": "mock",
        "formats": [
            {
                "format_id": "18",
                "ext": "mp4",
                "resolution": "640x360",
                "filesize": 500,
                "vcodec": "avc1",
                "acodec": "mp4a",
                "format_note": "medium",
            }
        ],
        "subtitles": {
            "en": [{"name": "English"}]
        },
        "automatic_captions": {
            "es": [{"name": "Spanish"}]
        },
    }

    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = mock_info

        info = await ProDLDownloader.get_info("https://example.com/video")
        assert info.title == "Mock Title"
        assert len(info.formats) == 1
        assert info.formats[0].format_id == "18"
        assert len(info.subtitles) == 2


@pytest.mark.asyncio
async def test_get_stream_info_mock():
    mock_info = {
        "url": "https://cdn.example.com/direct.mp4",
        "title": "Stream Title",
        "ext": "mp4",
        "filesize": 12345,
    }

    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = mock_info

        opts = DownloadOptions(url="https://example.com/video")
        stream_info = await ProDLDownloader.get_stream_info(opts)
        assert stream_info.url == "https://cdn.example.com/direct.mp4"
        assert stream_info.title == "Stream Title"


@pytest.mark.asyncio
async def test_download_mock(tmp_path):
    output_dir = str(tmp_path)
    mock_id = "test_vid_123"
    filepath = f"{output_dir}/{mock_id}.mp4"
    with open(filepath, "w") as f:
        f.write("dummy content")

    mock_info = {
        "id": mock_id,
        "title": "Downloaded Title",
        "ext": "mp4",
        "filesize": 13,
    }

    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = mock_info

        opts = DownloadOptions(
            url="https://example.com/video",
            output_dir=output_dir,
            subtitles=True,
            thumbnail=True,
            sponsorblock=True,
            sb_action="cut",
        )
        res = await ProDLDownloader.download(opts)
        assert res.title == "Downloaded Title"
        assert res.filename == f"{mock_id}.mp4"
        assert res.filepath == filepath
        assert res.filesize == 13
