import time
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any, cast

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

import auth
from config import settings
from database import init_db
from limiter import limiter
from logger import log, request_id_var
from routers.ai import router as ai_router
from routers.cars import router as cars_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("Checking and creating tables in a database...")
    await init_db()

    log.info("Connecting to Redis for background tasks...")
    app.state.redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))

    yield

    log.info("Disconnecting from Redis...")
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)

Instrumentator().instrument(app).expose(app)


async def add_request_id_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    req_id = str(uuid.uuid4())
    token = request_id_var.set(req_id)
    start_time = time.perf_counter()

    log.info("http_request_started", path=request.url.path, method=request.method)

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    log.info(
        "http_request_finished",
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration=round(process_time, 4),
    )

    response.headers["X-Request-ID"] = req_id
    request_id_var.reset(token)
    return response


app.add_middleware(BaseHTTPMiddleware, dispatch=add_request_id_middleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, cast(Any, _rate_limit_exceeded_handler))
app.add_middleware(SlowAPIMiddleware)

app.include_router(cars_router)
app.include_router(auth.router)
app.include_router(ai_router)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": 400,
            "detail": str(exc),
            "instance": str(request.url),
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()

    clean_detail = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in errors])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": 422,
            "detail": str(clean_detail),
            "instance": str(request.url),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    title = "Not Found" if exc.status_code == 404 else "HTTP Error"
    if exc.status_code == 401 or exc.status_code == 403:
        title = "Authentication Error"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url),
        },
    )


@app.get("/", include_in_schema=False)
def read_root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
