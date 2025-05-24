import pytest
import respx
from httpx import Response

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app 

from app.models import User
from app.main import fetch_users


@pytest.mark.asyncio
@respx.mock
async def test_fetch_users_mocked():
    mock_data = {
        "results": [
            {
                "gender": "male",
                "name": {"first": "John", "last": "Doe"},
                "email": "john.doe@example.com",
                "phone": "123-456-7890",
                "location": {"city": "New York", "country": "USA"},
                "picture": {"thumbnail": "http://example.com/photo.jpg"},
            }
        ]
    }

    respx.get("https://randomuser.me/api/", params={"results": "1"}).respond(
        json=mock_data,
        status_code=200
    )

    users = await fetch_users(batch_size=1)
    assert len(users) == 1
    user = users[0]
    assert isinstance(user, User)
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.location == "New York, USA"
