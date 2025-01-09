from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions import (
    APIServerError,
    InvalidAuthTokenError,
    NotPermittedError,
    VendorNotFoundError,
)


async def server_error_exc_handler(request: Request, exc: APIServerError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": "Internal server error", "details": exc.message})


async def invalid_auth_token_exc_handler(request: Request, exc: InvalidAuthTokenError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"error": "auth error", "details": exc.message})


async def vendor_not_found_exc_handler(request: Request, exc: VendorNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "Resource not found", "details": exc.message})


async def not_permitted_exc_handler(request: Request, exc: NotPermittedError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "Resource not permitted", "details": exc.message})


def init_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIServerError, server_error_exc_handler)
    app.add_exception_handler(InvalidAuthTokenError, invalid_auth_token_exc_handler)
    app.add_exception_handler(VendorNotFoundError, vendor_not_found_exc_handler)
    app.add_exception_handler(NotPermittedError, not_permitted_exc_handler)
