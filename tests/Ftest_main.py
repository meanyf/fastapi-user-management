import pytest
import httpx

@pytest.mark.asyncio
async def test_root():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/")
    assert response.status_code == 200
