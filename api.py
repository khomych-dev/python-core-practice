from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from routers.cars import router as cars_router

app = FastAPI()

app.include_router(cars_router)


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
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": 422,
            "detail": str(exc),
            "instance": str(request.url)
            
        }
    )
    
    
@app.get('/', include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")