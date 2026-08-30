import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from prodl_core.sponsorblock import get_segments


@pytest.mark.asyncio
async def test_get_segments_success():
    mock_data = [{"category": "sponsor", "segment": [10, 20]}]
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=mock_data)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        res = await get_segments("vid123", ["sponsor"])
        assert res == mock_data


@pytest.mark.asyncio
async def test_get_segments_404():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        res = await get_segments("vid123", ["sponsor"])
        assert res == []
