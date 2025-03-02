from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.dependencies.base_dependencies import get_log_repository
from src.exceptions import (
    APIServerError,
    InvalidAuthTokenError,
    InvalidCreateLogRequest,
    NotPermittedError,
    VendorNotFoundError,
)
from src.usecases.create_failure_log import CreateFailureLog


async def get_create_failure_log():
    log_repository = await get_log_repository()
    return CreateFailureLog(log_repository)

async def server_error_exc_handler(request: Request, exc: APIServerError) -> JSONResponse:
    create_failure_log = await get_create_failure_log()
    await create_failure_log(request)
    return JSONResponse(status_code=500, content={"error": "Internal server error", "details": exc.message})


async def invalid_auth_token_exc_handler(request: Request, exc: InvalidAuthTokenError) -> JSONResponse:
    create_failure_log = await get_create_failure_log()
    await create_failure_log(request)
    return JSONResponse(status_code=401, content={"error": "auth error", "details": exc.message})


async def vendor_not_found_exc_handler(request: Request, exc: VendorNotFoundError) -> JSONResponse:
    create_failure_log = await get_create_failure_log()
    await create_failure_log(request)
    return JSONResponse(status_code=404, content={"error": "Resource not found", "details": exc.message})


async def not_permitted_exc_handler(request: Request, exc: NotPermittedError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "Resource not permitted", "details": exc.message})


async def invalid_create_log_request_exc_handler(request: Request, exc: InvalidCreateLogRequest) -> JSONResponse:
    create_failure_log = await get_create_failure_log()
    await create_failure_log(request)
    return JSONResponse(status_code=200, content={"status": "fail"})


def init_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIServerError, server_error_exc_handler)
    app.add_exception_handler(InvalidAuthTokenError, invalid_auth_token_exc_handler)
    app.add_exception_handler(VendorNotFoundError, vendor_not_found_exc_handler)
    app.add_exception_handler(NotPermittedError, not_permitted_exc_handler)
    app.add_exception_handler(InvalidCreateLogRequest, invalid_create_log_request_exc_handler)
