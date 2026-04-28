from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user, require_admin
from dependencies import ai_rate_limiter, get_ai_service
from schemas import AgentRequest, AgentResponse
from services.ai_service import AIService, RepairReport

router = APIRouter(prefix="/api/v1/ai", tags=["AI Integration"])


class MechanicPrompt(BaseModel):
    text: str


class AIRepairResponse(BaseModel):
    message: str
    extracted_data: RepairReport


@router.post("/extract", response_model=AIRepairResponse, dependencies=[Depends(ai_rate_limiter)])
async def process_repair_text(
    prompt: MechanicPrompt,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    service: Annotated[AIService, Depends(get_ai_service)],
) -> AIRepairResponse:

    try:
        repair_data = await service.extract_repair_data(prompt.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    car = await service.car_service.repo.get_by_plate(repair_data.license_plate)

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


@router.post("/manager-insight", response_model=AgentResponse, dependencies=[Depends(ai_rate_limiter)])
async def manager_insight(
    request: AgentRequest,
    admin_user: Annotated[dict[str, Any], Depends(require_admin)],
    service: Annotated[AIService, Depends(get_ai_service)],
) -> Any:

    ai_answer = await service.run_manager_agent(request.prompt)

    return AgentResponse(answer=ai_answer)
