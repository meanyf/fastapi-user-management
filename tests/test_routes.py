# tests/test_minimal.py
import sys
import os
from httpx import AsyncClient
import pytest
from httpx._transports.asgi import ASGITransport
from fastapi.responses import HTMLResponse
from fastapi import Request, HTTPException
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000/") as client:
        response = await client.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_random():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000/") as client:
        response = await client.get("/homepage/random")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_user_route_mocked():
    with patch("app.main.get_user_from_db", new=AsyncMock(return_value={"id": 123, "name": "Test User"})):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://localhost:8000/") as client:
            response = await client.get("/homepage/123")
        assert response.status_code == 200