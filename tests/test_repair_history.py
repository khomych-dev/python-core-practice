import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CarDB, RepairHistoryDB, UserDB


@pytest.mark.asyncio
async def test_add_and_retrieve_repair_history_by_plate(db_session: AsyncSession) -> None:
    mechanic = UserDB(username="expert_mech", hashed_password="hashed_pw", role="mechanic")
    db_session.add(mechanic)

    target_plate = "AA1234BB"
    car = CarDB(plate_number=target_plate, brand="Toyota Camry", status="in_garage", mechanic_username="expert_mech")
    db_session.add(car)
    await db_session.commit()

    history_entry = RepairHistoryDB(
        car_plate_number=target_plate,
        mechanic_username="expert_mech",
        raw_text="The steering rack and coolant have been replaced.",
        ai_summary={"parts_replaced": ["steering rack", "coolant"], "labor_hours": 4.5, "requires_follow_up": False},
    )
    db_session.add(history_entry)
    await db_session.commit()

    stmt = select(RepairHistoryDB).where(RepairHistoryDB.car_plate_number == target_plate)
    result = await db_session.execute(stmt)
    saved_history = result.scalars().all()

    assert len(saved_history) == 1, "There should be exactly one service record for this car"

    db_record = saved_history[0]
    assert db_record.raw_text == "The steering rack and coolant have been replaced."
    assert db_record.ai_summary["parts_replaced"] == ["steering rack", "coolant"]
    assert db_record.mechanic_username == "expert_mech"


@pytest.mark.asyncio
async def test_cascade_delete_repair_history(db_session: AsyncSession) -> None:
    mechanic = UserDB(username="temp_mech", hashed_password="pw", role="mechanic")
    car = CarDB(plate_number="CX0000XX", brand="Unknown", status="done", mechanic_username="temp_mech")

    db_session.add_all([mechanic, car])
    await db_session.flush()

    history = RepairHistoryDB(
        car_plate_number="CX0000XX", mechanic_username="temp_mech", raw_text="Test", ai_summary={"test": True}
    )
    db_session.add(history)
    await db_session.commit()

    await db_session.delete(car)
    await db_session.commit()

    stmt = select(RepairHistoryDB).where(RepairHistoryDB.car_plate_number == "CX0000XX")
    result = await db_session.execute(stmt)
    remaining_history = result.scalars().all()

    assert len(remaining_history) == 0, "The repair history was supposed to be deleted along with the car via CASCADE"
