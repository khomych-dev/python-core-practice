import json
from typing import Any, cast

import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

import ai_tools
from config import settings

instructor_client = instructor.from_openai(AsyncOpenAI(api_key=settings.openai_api_key))

agent_client = AsyncOpenAI(api_key=settings.openai_api_key)


class RepairReport(BaseModel):
    license_plate: str = Field(
        description=("License plate number of the vehicle. Must be uppercase, no spaces. Example: AA1234BB")
    )
    work_description: str = Field(description="Brief description of the work performed.")
    parts_used: list[str] = Field(
        default_factory=list,
        description="List of spare parts used during the repair. Empty list if none.",
    )
    total_cost: float = Field(description=("Total cost of the repair in local currency. If not mentioned, use 0.0"))
    is_completed: bool = Field(
        description=("True if the mechanic implies the work is done. False if parts are ordered or work is pending.")
    )


async def extract_repair_data(mechanic_text: str) -> RepairReport:
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


async def run_manager_agent(prompt: str, db: AsyncSession) -> str:
    tools: list[dict[str, Any]] = [
        {
            "type": "function",
            "function": {
                "name": "get_cars",
                "description": "Get car details (owner, brand, status).",
                "parameters": {
                    "type": "object",
                    "properties": {"status": {"type": "string", "description": "Filter by 'in_garage' or 'released'."}},
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
                    "properties": {"plate_number": {"type": "string", "description": "Plate number, e.g., BC7777CB"}},
                    "required": ["plate_number"],
                },
            },
        },
    ]

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are the general manager of the service station. "
                "Your goal is to provide the MOST comprehensive answers possible."
                "RULE 1: If you are asked about a car, you MUST use the 'get_cars' "
                "tool to find out the owner and status."
                "RULE 2: After that, you MUST use the 'get_repair_history' "
                "tool to find out the full repair history of this car."
                "Only after gathering data from BOTH tools should you formulate your final answer."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    response = await agent_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=cast(Any, messages),
        tools=cast(Any, tools),
        tool_choice="auto",
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        messages.append(response_message.model_dump(exclude_none=True))

        for tool_call in response_message.tool_calls:
            tool_call_dict = tool_call.model_dump()

            func_name = tool_call_dict["function"]["name"]
            args = json.loads(tool_call_dict["function"]["arguments"])

            if func_name == "get_cars":
                result = await ai_tools.get_cars_in_garage(db, status=args.get("status"))
            elif func_name == "get_repair_history":
                result = await ai_tools.get_repair_history(db, plate_number=args.get("plate_number"))
            else:
                result = [{"error": f"Unknown function: {func_name}"}]

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_dict["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

        final_response = await agent_client.chat.completions.create(model="gpt-4o-mini", messages=cast(Any, messages))

        return final_response.choices[0].message.content or "No response from AI."

    return response_message.content if response_message.content else "No response."
