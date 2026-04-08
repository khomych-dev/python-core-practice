import pytest
from httpx import AsyncClient, ASGITransport

from api import app
from models import UserDB
from auth import get_current_user


@pytest.mark.asyncio
async def test_get_cars_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/cars/")

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


async def mock_mechanic_user():
    return {"username": "roki_test", "role": "mechanic"}

@pytest.mark.asyncio
async def test_register_car_success(db_session):
    app.dependency_overrides[get_current_user] = mock_mechanic_user

    test_user = UserDB(username="roki_test", hashed_password="fake_password", role="mechanic")
    db_session.add(test_user)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/cars/", json={
            "plate_number": "AA7777BB",
            "brand": "BMW",
            "owner": "Ivan"
        })

    assert response.status_code == 201
    assert "successfully registered" in response.json()["message"]

    app.dependency_overrides.clear()