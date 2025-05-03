from collections.abc import Callable
from functools import wraps

from src.exceptions import NotPermittedError

from fastapi import Depends
from starlette.requests import Request

from src.dependencies.base_dependencies import get_jwt_processor
from src.auth.jwt_processor import JwtProcessor
from src.db.models.models import UserOrm
from src.dependencies.dependencies import (
    get_user_repository,
)
from src.repositories.user_repository import UserRepository


def admin_required(func: Callable = None) -> Callable:
    def wrapper(func: Callable):
        @wraps(func)
        async def wrapped_func(*args, user, **kwargs):
            if user and not user.is_superuser or not user:
                raise NotPermittedError("у вас нет прав для выполнения запроса")
            return await func(*args, user=user, **kwargs)

        return wrapped_func

    if func:
        return wrapper(func)
    return wrapper


async def get_user(
    request: Request,
    jwt_processor: JwtProcessor = Depends(get_jwt_processor),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserOrm:
    token = request.session.get("token")
    if token:
        payload = jwt_processor.validate_token(token)
        if payload:
            return await user_repository.get(payload["sub"])

    return None
