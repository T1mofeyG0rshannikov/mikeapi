import csv
from collections.abc import Callable
from functools import wraps
from io import StringIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.auth.jwt_processor import JwtProcessor
from src.celery import create_traders_task, create_usernames_task
from src.db.models.models import TradersBuffer, UserOrm
from src.dependencies import (
    get_db,
    get_jwt_processor,
    get_user_repository,
)
from src.entites.trader import LoadTraderAction, TraderWatch
from src.exceptions import NotPermittedError
from src.repositories.user_repository import UserRepository

router = APIRouter(prefix="", tags=["traders"])


async def get_user(
    request: Request,
    jwt_processor: JwtProcessor = Depends(get_jwt_processor),
    user_repository: UserRepository = Depends(get_user_repository),
):
    token = request.session.get("token")
    if token:
        payload = jwt_processor.validate_token(token)
        if payload:
            return await user_repository.get(payload["sub"])

    return None


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


async def get_csv_file(
    csv_file: UploadFile = File(...),
):
    contents = await csv_file.read()
    decoded_contents = contents.decode("utf-8")

    csv_file = StringIO(decoded_contents)
    csv_data = csv.reader(csv_file)
    
    csvinput = []
    for row in csv_data:
        csvinput.append(row)

    return csvinput


async def get_txt_file(
    txt_file: UploadFile = File(...),
):
    contents = await txt_file.read()
    decoded_contents = contents.decode("utf-8")

    strings = []

    for line in decoded_contents.splitlines():
        if len(line) > 1:
            strings.append(line)

    return strings


@router.post("/traders/")
@admin_required
async def add_traders(
    user: Annotated[UserOrm, Depends(get_user)],
    csv_data=Depends(get_csv_file),
):
    create_traders_task.delay(csv_data)
    #return await create_traders(csv_data)


@router.post("/usernames/")
@admin_required
async def add_usernames(
    user: Annotated[UserOrm, Depends(get_user)],
    txt_data=Depends(get_txt_file),
):
    create_usernames_task.delay(txt_data)


@router.post("/subscribes/")
@admin_required
async def add_subscribes(
    user: Annotated[UserOrm, Depends(get_user)],
    txt_data=Depends(get_txt_file),
):
    create_usernames_task.delay(txt_data, watch=TraderWatch.on, action=LoadTraderAction.subscribes)
    #return await create_usernames(users=txt_data, watch=TraderWatch.on, action=LoadTraderAction.subscribes, app=vendor)


@router.delete("/clear-buffer/")
@admin_required
async def clear_buffer(
    user: Annotated[UserOrm, Depends(get_user)], request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):
    await db.execute(delete(TradersBuffer))
    await db.commit()
    request.session["buffer_size"] = 0

    return Response(status_code=200)
