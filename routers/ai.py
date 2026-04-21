from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai_service import RepairReport, extract_repair_data

router = APIRouter(prefix="/api/v1/ai", tags=["AI Integration"])


class MechanicPrompt(BaseModel):
    text: str


@router.post("/extract", response_model=RepairReport)
async def extract_data_from_text(prompt: MechanicPrompt) -> RepairReport:
    try:
        result = await extract_repair_data(prompt.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
