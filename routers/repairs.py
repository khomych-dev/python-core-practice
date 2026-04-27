from typing import Annotated, Any

from fastapi import APIRouter, Depends

from auth import get_current_user
from dependencies import get_repair_service
from schemas import RepairHistoryCreate, RepairHistoryResponse
from services.repair_service import RepairService

router = APIRouter(prefix="/api/v1/repairs", tags=["Repairs"])


@router.post("/history", response_model=RepairHistoryResponse)
async def confirm_and_save_repair(
    repair_data: RepairHistoryCreate,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    service: Annotated[RepairService, Depends(get_repair_service)],
) -> Any:

    saved_record = await service.save_history(repair_data=repair_data, username=current_user["username"])

    return saved_record
