from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class RepairHistoryBase(BaseModel):
    car_plate_number: str
    raw_text: str
    ai_summary: dict[str, Any]


class RepairHistoryCreate(RepairHistoryBase):
    mechanic_username: str | None = None


class RepairHistoryResponse(RepairHistoryBase):
    id: int
    mechanic_username: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
