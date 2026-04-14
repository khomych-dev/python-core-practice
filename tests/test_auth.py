import pytest
from httpx import AsyncClient, ASGITransport

from api import app
from models import UserDB
from security import get_password_hash, create_refresh_token


AUTH_PREFIX = "/auth"


@pytest.mark.asyncio
async def test_rate_limiter_login():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        for i in range(6):
            response = await ac.post(
                f"{AUTH_PREFIX}/login", data={"username": "fake", "password": "fake"}
            )

            if i < 5:
                assert response.status_code in [400, 422]
            else:
                assert response.status_code == 429
                assert "Rate limit exceeded" in response.json()["error"]


@pytest.mark.asyncio
async def test_refresh_token_success(db_session):
    """Перевіряємо, чи працює обмін довгого токена на новий короткий"""

    test_user = UserDB(
        username="refresh_tester",
        hashed_password=get_password_hash("secret"),
        role="mechanic",
    )
    db_session.add(test_user)
    await db_session.commit()

    valid_refresh_token = create_refresh_token(data={"sub": "refresh_tester"})

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            f"{AUTH_PREFIX}/refresh", json={"refresh_token": valid_refresh_token}
        )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" not in data
    assert data["token_type"] == "bearer"
