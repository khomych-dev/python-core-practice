import pytest
from httpx import AsyncClient, ASGITransport

from api import app
from models import UserDB
from security import get_password_hash, create_refresh_token

# УВАГА: Якщо твій auth_router підключений в api.py з префіксом /api/v1, 
# зміни тут "/auth/login" на "/api/v1/auth/login"
AUTH_PREFIX = "/auth" 

@pytest.mark.asyncio
async def test_rate_limiter_login():
    """Перевіряємо, чи блокує сервер спам запитами (більше 5 на хвилину)"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        # Робимо 6 запитів підряд
        for i in range(6):
            # Передаємо фейкові дані (нам байдуже на пароль, ми тестуємо сам ліміт)
            response = await ac.post(f"{AUTH_PREFIX}/login", data={"username": "fake", "password": "fake"})
            
            if i < 5:
                # Перші 5 запитів мають пройти лімітер (отримають 400 або 422)
                assert response.status_code in [400, 422]
            else:
                # 6-й запит має бути жорстко заблокований
                assert response.status_code == 429
                assert "Rate limit exceeded" in response.json()["error"]


@pytest.mark.asyncio
async def test_refresh_token_success(db_session):
    """Перевіряємо, чи працює обмін довгого токена на новий короткий"""
    
    # 1. Створюємо тестового юзера в базі даних
    test_user = UserDB(
        username="refresh_tester", 
        hashed_password=get_password_hash("secret"), 
        role="mechanic"
    )
    db_session.add(test_user)
    await db_session.commit()

    # 2. Генеруємо для нього справжній refresh_token
    valid_refresh_token = create_refresh_token(data={"sub": "refresh_tester"})

    # 3. Йдемо в "обмінник"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"{AUTH_PREFIX}/refresh",
            json={"refresh_token": valid_refresh_token}
        )

    # 4. Перевіряємо, чи видали нам новий квиток
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" not in data # Обмінник не має видавати новий рефреш
    assert data["token_type"] == "bearer"