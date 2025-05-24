import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from fastapi import status
from httpx import ASGITransport
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app 

@pytest.mark.asyncio
async def test_load_users_post_with_asgi_transport():
    with patch("app.main.fetch_and_save_users", new=AsyncMock()) as mock_fetch_save:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://localhost:8000/") as client:
            response = await client.post("/load", data={"count": "5"})
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/"
        mock_fetch_save.assert_awaited_once_with(5)
