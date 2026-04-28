from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from logger import log
from models import RepairHistoryDB
from repositories.repair_repository import RepairRepository
from schemas import RepairHistoryCreate


class RepairService:
    def __init__(self, repo: RepairRepository):
        self.repo = repo

    async def save_history(self, repair_data: RepairHistoryCreate, username: str) -> RepairHistoryDB:
        new_record = RepairHistoryDB(
            car_plate_number=repair_data.car_plate_number,
            mechanic_username=username,
            raw_text=repair_data.raw_text,
            ai_summary=repair_data.ai_summary,
        )

        try:
            saved_record = await self.repo.add(new_record)
            log.info(
                "repair_history_saved",
                username=username,
                plate_number=repair_data.car_plate_number,
                action_type="audit",
            )
            return saved_record

        except SQLAlchemyError as e:
            log.error("db_error_repair_history", error=str(e))
            raise HTTPException(
                status_code=400,
                detail="An error occurred while saving to the database. "
                "Please verify the data (for example, check if a car with that license plate number exists).",
            ) from e
