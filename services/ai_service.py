import json
from typing import Any

from fastapi import HTTPException, status
from langfuse import observe
from langfuse.openai import AsyncOpenAI  # type: ignore
from pydantic import BaseModel, Field

from config import settings
from services.car_service import CarService
from services.repair_service import RepairService
from tools.core import ToolRegistry
from tools.garage_tools import GetCarsTool, GetRepairHistoryTool

agent_client = AsyncOpenAI(api_key=settings.openai_api_key)


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

        self.registry = ToolRegistry()
        self.registry.register(GetCarsTool(self.car_service))
        self.registry.register(GetRepairHistoryTool(self.repair_service))

    @observe(name="Extract Repair Data (Structured Output)")
    async def extract_repair_data(self, mechanic_text: str) -> RepairReport:
        report = await agent_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=RepairReport,
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

        parsed_data = report.choices[0].message.parsed

        if parsed_data is None:
            raise ValueError("Model refused or failed to output structured data.")

        invalid_plates = ["UNKNOWN", "NONE", "N/A", ""]
        if parsed_data.license_plate.upper() in invalid_plates or len(parsed_data.license_plate) < 3:
            raise ValueError(
                "Rejected: The text does not contain a valid license plate number or does not pertain to repairs. "
                "Please provide the vehicle identification number and details of the work performed."
            )

        return parsed_data  # type: ignore[no-any-return]

    @observe(name="Manager Agent Loop")
    async def run_manager_agent(self, prompt: str) -> str:
        tools = self.registry.get_tools_definitions()

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
            api_kwargs: dict[str, Any] = {
                "model": "gpt-4o-mini",
                "messages": messages,
            }

            if tools:
                api_kwargs["tools"] = tools
                api_kwargs["tool_choice"] = "auto"

            try:
                response = await agent_client.chat.completions.create(**api_kwargs)
            except Exception as e:
                print(f"OpenAI API Error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="The AI gateway is temporarily unavailable. The issue is on the provider's end (OpenAI).",
                ) from e

            response_message = response.choices[0].message

            if not response_message.tool_calls:
                return response_message.content or "No response."

            messages.append(response_message.model_dump(exclude_none=True))

            for tool_call in response_message.tool_calls:
                tool_call_dict = tool_call.model_dump()
                func_name = tool_call_dict["function"]["name"]
                arguments = tool_call_dict["function"]["arguments"]

                result = await self.registry.call_tool(func_name, arguments)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_dict["id"],
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    }
                )

        return (
            "The AI exceeded the step limit (maximum number of iterations) and was unable to generate a final answer."
        )
