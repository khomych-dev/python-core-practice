import asyncio
from arq.connections import RedisSettings

from config import settings


async def send_notification_task(ctx, email: str, message: str):
    print(f"[{email}] I'm starting to generate and send the email...")

    await asyncio.sleep(5)

    print(f"[{email}] Success! The email '{message}' has been sent successfully.")
    return True


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)

    functions = [send_notification_task]
