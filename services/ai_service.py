import json
from typing import Any, cast

import instructor
from langfuse import observe
from langfuse.openai import AsyncOpenAI  # type: ignore
from pydantic import BaseModel, Field

from config import settings
from services.car_service import CarService
from services.repair_service import RepairService

agent_client = AsyncOpenAI(api_key=settings.openai_api_key)
instructor_client = instructor.from_openai(agent_client)


class RepairReport(BaseModel):
    license_plate: str = Field(
        description="License plate number of the vehicle. Must be uppercase, no spaces. Example: AA1234BB"
    )
    work_description: str = Field(description="Brief description of the work performed.")
    parts_used: list[str] = Field(
        default_factory=list,
        description="List of spare parts used during the repair. Empty list if none.",
    )
    total_cost: float = Field(description="Total cost of the repair in local currency. If not mentioned, use 0.0")
    is_completed: bool = Field(
        description="True if the mechanic implies the work is done. False if parts are ordered or work is pending."
    )


class AIService:
    def __init__(self, car_service: CarService, repair_service: RepairService):
        self.car_service = car_service
        self.repair_service = repair_service

    @observe(name="Extract Repair Data (Structured Output)")
    async def extract_repair_data(self, mechanic_text: str) -> RepairReport:
        report = await instructor_client.chat.completions.create(
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

    @observe(name="Manager Agent Loop")
    async def run_manager_agent(self, prompt: str) -> str:
        tools: list[dict[str, Any]] = [
            {
                "type": "function",
                "function": {
                    "name": "get_cars",
                    "description": "Get car details (owner, brand, status).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "description": "Filter by 'in_garage' or 'released'."},
                            "plate_number": {"type": "string", "description": "Filter by plate number, e.g., BC7777CB"},
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_repair_history",
                    "description": "Get detailed repair history for a specific car.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plate_number": {"type": "string", "description": "Plate number, e.g., BC7777CB"}
                        },
                        "required": ["plate_number"],
                    },
                },
            },
        ]

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You're the service center manager. Please provide as much detail as possible. "
                    "If someone asks about a car, be sure to check both its status (get_cars) "
                    "and its repair history (get_repair_history). Respond in English."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        max_iterations = 5
        for _ in range(max_iterations):
            response = await agent_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=cast(Any, messages),
                tools=cast(Any, tools),
                tool_choice="auto",
            )

            response_message = response.choices[0].message

            if not response_message.tool_calls:
                return response_message.content or "No response."

            messages.append(response_message.model_dump(exclude_none=True))

            for tool_call in response_message.tool_calls:
                tool_call_dict = tool_call.model_dump()
                func_name = tool_call_dict["function"]["name"]
                args = json.loads(tool_call_dict["function"]["arguments"])

                result: list[dict[str, Any]] = []

                if func_name == "get_cars":
                    plate = args.get("plate_number")
                    status_filter = args.get("status")

                    if plate:
                        car = await self.car_service.repo.get_by_plate(plate)
                        cars = [car] if car else []
                    elif status_filter:
                        cars_seq = await self.car_service.get_cars_by_status(status_filter)
                        cars = list(cars_seq)
                    else:
                        cars_seq = await self.car_service.get_all_cars()
                        cars = list(cars_seq)

                    if cars:
                        result = [
                            {
                                "plate_number": c.plate_number,
                                "brand": c.brand,
                                "owner": c.owner,
                                "status": c.status,
                                "mechanic": c.mechanic_username,
                            }
                            for c in cars
                        ]
                    else:
                        result = [{"error": "No cars found matching the criteria"}]

                elif func_name == "get_repair_history":
                    plate = args.get("plate_number")
                    if plate:
                        history = await self.repair_service.repo.get_by_car_plate(plate)
                        if history:
                            result = [
                                {
                                    "mechanic": h.mechanic_username,
                                    "text": h.raw_text,
                                    "date": h.created_at.isoformat() if h.created_at else None,
                                }
                                for h in history
                            ]
                        else:
                            result = [{"message": "No history found"}]
                    else:
                        result = [{"error": "plate_number is required"}]

                else:
                    result = [{"error": f"Unknown function: {func_name}"}]

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_dict["id"],
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    }
                )

        return "The AI exceeded the character limit and was unable to generate a response."
