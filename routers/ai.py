from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_service import RepairReport, extract_repair_data
from auth import get_current_user, get_db
from models import CarDB

router = APIRouter(prefix="/api/v1/ai", tags=["AI Integration"])


class MechanicPrompt(BaseModel):
    text: str


class AIRepairResponse(BaseModel):
    message: str
    extracted_data: RepairReport


@router.post("/extract", response_model=AIRepairResponse)
async def process_repair_text(
    prompt: MechanicPrompt,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AIRepairResponse:

    try:
        repair_data = await extract_repair_data(prompt.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    stmt = select(CarDB).where(CarDB.plate_number == repair_data.license_plate)
    result = await db.execute(stmt)
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(
            status_code=404,
            detail=(
                f"The AI recognized the number {repair_data.license_plate}, "
                "but there isn't a car like that in the garage."
            ),
        )

    if repair_data.is_completed:
        msg = (
            f"The report was generated successfully. Vehicle {car.plate_number} "
            "can be forwarded to the administrator for release from the garage."
        )
    else:
        msg = f"Data recognized. Repairs on the car {car.plate_number} are still in progress."

    return AIRepairResponse(message=msg, extracted_data=repair_data)
