import httpx
import pytest
from test_constants import API_URL


@pytest.mark.asyncio
async def test_healthcheck():
    async with httpx.AsyncClient(base_url=API_URL) as client:
        response = await client.get('/docs')
    assert response.status_code == 200
