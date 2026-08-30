import httpx


async def fetch_thumbnail(url: str) -> bytes:
    """
    Download the thumbnail image as raw bytes.
    Use httpx async client.
    Just GET the URL and return response.content.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content
