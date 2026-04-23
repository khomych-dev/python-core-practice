import os
from typing import Any

from arq.connections import RedisSettings
from sqlalchemy import select

from ai_service import agent_client
from config import settings
from database import AsyncSessionLocal
from logger import log
from models import RepairHistoryDB


async def generate_invoice_task(ctx: dict[str, Any], plate_number: str) -> bool:
    log.info("invoice_generation_started", car=plate_number)

    async with AsyncSessionLocal() as db:
        stmt = select(RepairHistoryDB).where(RepairHistoryDB.car_plate_number == plate_number)
        result = await db.execute(stmt)
        records = result.scalars().all()

    if not records:
        log.warning("no_repair_history_found", car=plate_number)
        return False

    history_text = "\n".join([f"- {r.raw_text}" for r in records])

    try:
        response = await agent_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional service center manager. "
                    "Your task is to generate a professional invoice for the customer (in Markdown format) "
                    "based on their repair history. "
                    "Include a list of services performed, the parts used, and the total amount. Be polite.",
                },
                {
                    "role": "user",
                    "content": f"Generate a final report for the vehicle with license plate number {plate_number}. "
                    f"Here is the raw data from the mechanics:\n{history_text}",
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
        f.write(invoice_text or "Помилка генерації тексту.")

    log.info("invoice_generation_success", car=plate_number, file_path=file_path)
    return True


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [generate_invoice_task]
