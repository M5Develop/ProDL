import json
import httpx


async def get_segments(video_id: str, categories: list[str]) -> list[dict]:
    """
    Call SponsorBlock API directly (optional utility).
    GET https://sponsor.ajay.app/api/skipSegments
        ?videoID={video_id}
        &categories={json_encoded_categories}

    Use httpx async client.
    Return list of segment dicts as-is from the API.
    If 404 (no segments found) → return empty list.
    """
    encoded_categories = json.dumps(categories)
    params = {
        "videoID": video_id,
        "categories": encoded_categories,
    }
    url = "https://sponsor.ajay.app/api/skipSegments"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json()
