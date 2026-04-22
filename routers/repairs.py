from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import repair_service
from auth import get_current_user, get_db
from schemas import RepairHistoryCreate, RepairHistoryResponse

router = APIRouter(prefix="/api/v1/repairs", tags=["Repairs"])


@router.post("/history", response_model=RepairHistoryResponse)
async def confirm_and_save_repair(
    repair_data: RepairHistoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> Any:
    repair_data.mechanic_username = current_user["username"]

    try:
        saved_record = await repair_service.save_history_to_db(db, repair_data)
        return saved_record

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}") from e
