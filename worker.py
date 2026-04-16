import asyncio
from typing import Any

from arq.connections import RedisSettings

from config import settings
from logger import log


async def send_notification_task(ctx: dict[str, Any], email: str, message: str) -> bool:
    log.info("email_sending_started", email=email)

    await asyncio.sleep(5)

    log.info("email_sending_success", email=email, message=message)
    return True


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [send_notification_task]
