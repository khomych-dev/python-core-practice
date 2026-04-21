from typing import cast

import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from config import settings

client = instructor.from_openai(AsyncOpenAI(api_key=settings.openai_api_key))


class RepairReport(BaseModel):
    license_plate: str = Field(
        description=(
            "License plate number of the vehicle. "
            "Must be uppercase, no spaces. Example: AA1234BB"
        )
    )
    work_description: str = Field(
        description="Brief description of the work performed."
    )
    parts_used: list[str] = Field(
        default_factory=list,
        description="List of spare parts used during the repair. Empty list if none.",
    )
    total_cost: float = Field(
        description=(
            "Total cost of the repair in local currency. If not mentioned, use 0.0"
        )
    )
    is_completed: bool = Field(
        description=(
            "True if the mechanic implies the work is done. "
            "False if parts are ordered or work is pending."
        )
    )


async def extract_repair_data(mechanic_text: str) -> RepairReport:
    report = await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=RepairReport,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise automotive assistant. Extract structured "
                    "repair details from the mechanic's raw text. Never invent data."
                ),
            },
            {
                "role": "user",
                "content": mechanic_text,
            },
        ],
        temperature=0.1,
    )
    return cast(RepairReport, report)
