from typing import Annotated, Any

import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user, get_db
from config import settings
from models import ApiKeyDB
from repositories.car_repository import CarRepository
from repositories.invoice_repository import InvoiceRepository
from repositories.repair_repository import RepairRepository
from services.ai_service import AIService
from services.billing_service import BillingService
from services.car_service import CarService
from services.repair_service import RepairService

redis_client = redis.from_url(str(settings.redis_url), decode_responses=True)  # type: ignore[no-untyped-call]

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    key_header: str | None = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> ApiKeyDB:
    if not key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is missing in headers (X-API-Key)",
        )

    stmt = select(ApiKeyDB).where(ApiKeyDB.key == key_header, ApiKeyDB.is_active.is_(True))
    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API Key",
        )

    return api_key


async def ai_rate_limiter(current_user: Annotated[dict[str, Any], Depends(get_current_user)]) -> dict[str, Any]:
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
    return getattr(request.app.state, "redis_pool", None)


async def get_car_service(
    db: AsyncSession = Depends(get_db),
    redis_pool: Any = Depends(get_redis_pool),
) -> CarService:
    repo = CarRepository(db)
    return CarService(repo, redis_pool)


async def get_repair_service(db: AsyncSession = Depends(get_db)) -> RepairService:
    repo = RepairRepository(db)
    return RepairService(repo)


async def get_ai_service(
    car_service: CarService = Depends(get_car_service),
    repair_service: RepairService = Depends(get_repair_service),
) -> AIService:
    return AIService(car_service, repair_service)


async def get_billing_service(db: AsyncSession = Depends(get_db)) -> BillingService:
    repo = InvoiceRepository(db)
    return BillingService(repo)
