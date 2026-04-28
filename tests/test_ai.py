from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api import app
from auth import get_current_user
from models import CarDB, UserDB
from services.ai_service import RepairReport


async def mock_mechanic_user() -> dict[str, str]:
    return {"username": "ai_tester", "role": "mechanic"}


@pytest.mark.asyncio
@patch("services.ai_service.AIService.extract_repair_data")
async def test_ai_extract_repair_data_success(mock_extract: AsyncMock, db_session: AsyncSession) -> None:
    app.dependency_overrides[get_current_user] = mock_mechanic_user

    try:
        test_user = UserDB(username="ai_tester", hashed_password="fake", role="mechanic")
        db_session.add(test_user)

        test_car = CarDB(
            plate_number="AI9999OK",
            brand="Toyota",
            owner="TestOwner",
            status="in_garage",
            mechanic_username="ai_tester",
        )
        db_session.add(test_car)
        await db_session.commit()

        fake_report = RepairReport(
            license_plate="AI9999OK",
            work_description="Changed oil and filters",
            parts_used=["oil", "filter"],
            total_cost=150.0,
            is_completed=True,
        )
        mock_extract.return_value = fake_report

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/ai/extract",
                json={"text": "I changed the oil and filter on AI9999OK. Total is 150. The car is ready."},
            )

        assert response.status_code == 200
        data = response.json()

        assert data["extracted_data"]["license_plate"] == "AI9999OK"
        assert data["extracted_data"]["is_completed"] is True
        assert "generated successfully" in data["message"]

    finally:
        app.dependency_overrides.pop(get_current_user, None)
