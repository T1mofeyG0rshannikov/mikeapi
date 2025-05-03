from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.exceptions import APIServerError
import os

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        debug = os.environ.get("DEBUG", False)

        if debug:
            return super().dispatch(request, call_next)
        
        try:
            return await call_next(request)
        except Exception as e:
            raise APIServerError("Что-то пошло не так")
