from typing import Annotated, Any

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status

from auth import get_current_user
from config import settings

redis_client = redis.from_url(str(settings.redis_url), decode_responses=True)


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
        print(f"Redis Error in Rate Limiter: {e}")
        pass

    return current_user
