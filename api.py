from fastapi import FastAPI, status, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from routers.cars import router as cars_router
import auth
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from limiter import limiter

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore
app.add_middleware(SlowAPIMiddleware)

app.include_router(cars_router)
app.include_router(auth.router)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": 400,
            "detail": str(exc),
            "instance": str(request.url)
        }
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    clean_detail = "; ".join(
        [f"{err['loc'][-1]}: {err['msg']}" for err in errors])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": 422,
            "detail": str(clean_detail),
            "instance": str(request.url)

        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
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
            "instance": str(request.url)
        }
    )


@app.get('/', include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")
