from typing import Annotated, Any

import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user, get_db
from config import settings
from repositories.car_repository import CarRepository
from services.car_service import CarService

redis_client = redis.from_url(str(settings.redis_url), decode_responses=True)  # type: ignore[no-untyped-call]


async def ai_rate_limiter(current_user: Annotated[dict[str, Any], Depends(get_current_user)]) -> dict[str, Any]:
    """
    Limit: 5 requests per minute per user.
    """
    username = current_user.get("username")
    key = f"rate_limit:ai:user:{username}"

    try:
        requests = await redis_client.incr(key)

        if requests == 1:
            await redis_client.expire(key, 60)

        if requests > 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests to the AI. Please try again in a minute.",
            )

    except redis.RedisError as e:
        print(f"Redis error in Rate Limiter: {e}")
        pass

    return current_user


async def get_redis_pool(request: Request) -> Any:
    """
    Retrieves the global ARQ pool that we create when the server starts in main.py.
    """
    return getattr(request.app.state, "redis_pool", None)


async def get_car_service(
    db: AsyncSession = Depends(get_db),
    redis_pool: Any = Depends(get_redis_pool),
) -> CarService:
    repo = CarRepository(db)
    return CarService(repo, redis_pool)
