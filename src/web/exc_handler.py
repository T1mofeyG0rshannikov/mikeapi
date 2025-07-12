from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.dependencies.repos_container import ReposContainer
from src.exceptions import (
    APIServerError,
    InvalidAuthTokenError,
    InvalidCreateLogRequest,
    NotPermittedError,
    VendorNotFoundError,
)
from src.usecases.create_failure_log import CreateFailureLog


async def create_failure_log(request: Request) -> None:
    log_repository = await ReposContainer.deal_repository()
    usecase = CreateFailureLog(log_repository)
    await usecase(request)

async def server_error_exc_handler(request: Request, exc: APIServerError) -> JSONResponse:
    await create_failure_log(request)
    return JSONResponse(status_code=500, content={"error": "Internal server error", "details": exc.message})


async def invalid_auth_token_exc_handler(request: Request, exc: InvalidAuthTokenError) -> JSONResponse:
    await create_failure_log(request)
    return JSONResponse(status_code=401, content={"error": "auth error", "details": exc.message})


async def vendor_not_found_exc_handler(request: Request, exc: VendorNotFoundError) -> JSONResponse:
    await create_failure_log(request)
    return JSONResponse(status_code=404, content={"error": "Resource not found", "details": exc.message})


async def not_permitted_exc_handler(request: Request, exc: NotPermittedError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"error": "Resource not permitted", "details": exc.message})


async def invalid_create_log_request_exc_handler(request: Request, exc: InvalidCreateLogRequest) -> JSONResponse:
    await create_failure_log(request)
    return JSONResponse(status_code=200, content={"status": "fail", "details": exc.message})


def init_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIServerError, server_error_exc_handler)
    app.add_exception_handler(InvalidAuthTokenError, invalid_auth_token_exc_handler)
    app.add_exception_handler(VendorNotFoundError, vendor_not_found_exc_handler)
    app.add_exception_handler(NotPermittedError, not_permitted_exc_handler)
    app.add_exception_handler(InvalidCreateLogRequest, invalid_create_log_request_exc_handler)
