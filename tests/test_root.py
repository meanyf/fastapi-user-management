# tests/test_minimal.py
import sys
import os
from httpx import AsyncClient
import pytest
from httpx._transports.asgi import ASGITransport

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

@pytest.mark.asyncio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost:8000/") as client:
        response = await client.get("/")
    assert response.status_code == 200