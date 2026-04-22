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
                "description": "Retrieves a list of cars from the database. "
                "Use this to answer questions about cars, their brands, owners, or statuses.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Optional filter for car status. "
                            "Valid values are usually 'in_garage' or 'released'.",
                        }
                    },
                    "required": [],
                },
            },
        }
    ]

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": "You are a helpful garage manager assistant. "
            "Use the supplied tools to answer questions about the garage. Provide concise and accurate answers.",
        },
        {"role": "user", "content": prompt},
    ]

    response = await agent_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,  # pyright: ignore
        tools=tools,  # pyright: ignore
        tool_choice="auto",
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        tool_call = response_message.tool_calls[0]

        tool_call_dict = tool_call.model_dump()

        if tool_call_dict["function"]["name"] == "get_cars":
            args = json.loads(tool_call_dict["function"]["arguments"])
            status_filter = args.get("status")

            cars_data = await ai_tools.get_cars_in_garage(db, status=status_filter)

            messages.append(response_message.model_dump(exclude_none=True))

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_dict["id"],
                    "content": json.dumps(cars_data, ensure_ascii=False),
                }
            )

            final_response = await agent_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,  # pyright: ignore
            )

            content = final_response.choices[0].message.content
            return content if content else "The AI was unable to generate a response."

    return response_message.content if response_message.content else "No response."
