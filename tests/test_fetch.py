from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import httpx

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
@patch("app.main.SessionLocal")  # Мокаем фабрику сессий, не AsyncMock, а просто MagicMock
async def test_fetch_and_save_users(mock_session_local, mock_get):
    # Мок ответа HTTP
    mock_get.return_value = AsyncMock(
        status_code=200,
        json=AsyncMock(return_value={
            "results": [
                {
                    "gender": "female",
                    "name": {"first": "Alice", "last": "Smith"},
                    "email": "alice@example.com",
                    "phone": "123456789",
                    "location": {"city": "City", "country": "Country"},
                    "picture": {"thumbnail": "https://example.com/thumb.jpg"}
                }
            ]
        }),
        raise_for_status=MagicMock()
    )

    # Мокаем экземпляр сессии с async контекстом
    mock_session_instance = AsyncMock()
    # Важно: mock_session_instance должен поддерживать async контекстный менеджер
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None

    # Фабрика сессий возвращает мок сессии
    mock_session_local.return_value = mock_session_instance

    # Вызов функции
    await fetch_and_save_users(batch_size=1)

    # Проверяем вызов HTTP запроса
    mock_get.assert_awaited_once_with("https://randomuser.me/api/?results=1")

    # Проверяем, что add был вызван (add — sync метод, поэтому вызывается без await)
    assert mock_session_instance.add.call_count > 0

    # Проверяем, что commit был await’нут
    mock_session_instance.commit.assert_awaited_once()
