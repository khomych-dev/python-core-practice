import os
from typing import Any

from arq.connections import RedisSettings
from langfuse import get_client, observe
from sqlalchemy import select

from ai_service import agent_client
from config import settings
from database import AsyncSessionLocal
from logger import log
from models import RepairHistoryDB


@observe()
async def generate_invoice_task(ctx: dict[str, Any], raw_plate_number: str) -> bool:
    plate_number = raw_plate_number.strip()
    log.info("invoice_generation_started", car=plate_number)

    async with AsyncSessionLocal() as db:
        debug_stmt = select(RepairHistoryDB.car_plate_number)
        debug_result = await db.execute(debug_stmt)
        all_plates = debug_result.scalars().all()
        log.info("debug_all_plates_in_db", plates=all_plates)

        stmt = select(RepairHistoryDB).where(RepairHistoryDB.car_plate_number == plate_number)
        result = await db.execute(stmt)
        records = result.scalars().all()

    if not records:
        log.warning("no_repair_history_found", car=plate_number)
        return False

    history_text = "\n".join(
        [
            f"- Date: {r.created_at.strftime('%Y-%m-%d')}. Mechanic: {r.mechanic_username}. Works: {r.raw_text}"
            for r in records
        ]
    )

    try:
        response = await agent_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the general manager of a high-end auto service center. "
                        "Your task is to generate the final "
                        "an invoice for the client in Markdown format.\n"
                        "MANDATORY RULES:\n"
                        "1. Use the actual date and the mechanic's name from the provided data "
                        "(add the mechanic's name at the end of the document).\n"
                        "2. If you have not been provided with specific data (such as prices for services or parts), "
                        "it is STRICTLY PROHIBITED to make them up. "
                        "Instead, write 'data missing' in the corresponding table fields or in the total."
                        "3. Be sure to complete the entire document layout "
                        "(including columns for prices and the total amount), applying Rule 3 for unknown figures."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Generate an invoice for the car with license plate number {plate_number}. "
                    f"Here is the raw data from the database:\n{history_text}",
                },
            ],
            temperature=0.2,
        )
        invoice_text = response.choices[0].message.content

    except Exception as e:
        log.error("ai_invoice_generation_failed", error=str(e))
        return False

    os.makedirs("invoices", exist_ok=True)
    file_path = f"invoices/{plate_number}_invoice.md"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(invoice_text or "Text generation error.")

    log.info("invoice_generation_success", car=plate_number, file_path=file_path)

    get_client().flush()

    return True


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [generate_invoice_task]
