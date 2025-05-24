import pytest
import respx
from httpx import Response
from httpx import AsyncClient
from httpx import ASGITransport

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app 

@pytest.mark.asyncio
@respx.mock
async def test_random_user_page():
    mock_data = {
    "results": [{
        "gender": "male",
        "name": {"first": "Test", "last": "User"},
        "email": "test@example.com",
        "phone": "+1-202-555-0136",
        "location": {
            "city": "Test City",
            "country": "Testland"
        },
        "picture": {
            "thumbnail": "https://example.com/photo_thumb.jpg",
            "large": "https://example.com/photo_large.jpg"
        }
    }]
}

    respx.get("https://randomuser.me/api/").respond(
        json=mock_data,
        status_code=200
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000/") as client:
        response = await client.get("/homepage/random")

    assert response.status_code == 200
    assert "Test" in response.text
    assert "User" in response.text
    assert "test@example.com" in response.text
