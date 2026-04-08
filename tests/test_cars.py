import pytest
from httpx import AsyncClient, ASGITransport

from api import app

@pytest.mark.asyncio
async def test_get_cars_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/cars/")
        
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}