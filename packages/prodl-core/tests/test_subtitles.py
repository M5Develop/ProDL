import pytest
from unittest.mock import patch
from prodl_core.subtitles import list_subtitles


@pytest.mark.asyncio
async def test_list_subtitles_mock():
    mock_info = {
        "subtitles": {
            "en": [{"name": "English"}]
        },
        "automatic_captions": {
            "fr": [{"name": "French"}]
        },
    }

    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = mock_info

        subs = await list_subtitles("https://example.com/video")
        assert len(subs) == 2
        assert subs[0].lang == "en"
        assert subs[0].is_auto is False
        assert subs[1].lang == "fr"
        assert subs[1].is_auto is True
