import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from prodl_core.thumbnail import fetch_thumbnail


@pytest.mark.asyncio
async def test_fetch_thumbnail():
    mock_bytes = b"fake image bytes"
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.content = mock_bytes
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        res = await fetch_thumbnail("https://example.com/thumb.jpg")
        assert res == mock_bytes
