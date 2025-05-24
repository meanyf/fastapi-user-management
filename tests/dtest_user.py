import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from starlette.status import HTTP_200_OK
from app.main import app
from app.db import SessionLocal
from app.models import User

@pytest.mark.asyncio
async def test_get_existing_user():
    async with SessionLocal() as session:
        new_user = None
        try:
            new_user = User(
                first_name="Alice",
                last_name="Smith",
                email="alice@example.com",
                gender="female",
                phone="123456789",
                location="City, Country",
                photo_url="https://example.com/photo.jpg"
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            user_id = new_user.id

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://localhost:8000/") as client:
                response = await client.get(f"/user/{user_id}")

            assert response.status_code == HTTP_200_OK
            assert "Alice" in response.text
            assert "Smith" in response.text
            assert "alice@example.com" in response.text

        finally:
            if new_user is not None:
                # Заново получить пользователя из базы и удалить
                user_to_delete = await session.get(User, new_user.id)
                if user_to_delete is not None:
                    await session.delete(user_to_delete)
                    await session.commit()
