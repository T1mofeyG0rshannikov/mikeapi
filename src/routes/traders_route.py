import csv
from collections.abc import Callable
from functools import wraps
from io import StringIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from starlette.requests import Request

from src.auth.jwt_processor import JwtProcessor
from src.create_traders import CreateTraders
from src.create_usernames import AddUsernames, CreateUsernameDTO
from src.db.models.models import UserOrm
from src.dependencies import (
    get_create_traders,
    get_create_usernames,
    get_jwt_processor,
    get_user_repository,
    get_vendor_repository,
)
from src.entites.trader import TraderWatch
from src.exceptions import NotPermittedError
from src.repositories.user_repository import UserRepository
from src.repositories.vendor_repository import VendorRepository

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

    return csv_data


async def get_txt_file(
    txt_file: UploadFile = File(...),
):
    contents = await txt_file.read()
    decoded_contents = contents.decode("utf-8")

    strings = []

    for line in decoded_contents.splitlines():
        if len(line) > 1:
            strings.append(line)

    users = []

    for i in range(0, len(strings) // 2, 2):
        users.append(CreateUsernameDTO(username=strings[i], data=strings[i + 1]))

    users = sorted(users, key=lambda u: u.username)

    return users


@router.post("/traders/")
@admin_required
async def add_traders(
    user: Annotated[UserOrm, Depends(get_user)],
    create_traders: Annotated[CreateTraders, Depends(get_create_traders)],
    csv_data=Depends(get_csv_file),
):
    return await create_traders(csv_data)


@router.post("/usernames/")
@admin_required
async def add_usernames(
    user: Annotated[UserOrm, Depends(get_user)],
    create_usernames: Annotated[AddUsernames, Depends(get_create_usernames)],
    txt_data=Depends(get_txt_file),
):
    return await create_usernames(txt_data)


@router.post("/subscribes/")
@admin_required
async def add_subscribes(
    user: Annotated[UserOrm, Depends(get_user)],
    create_usernames: Annotated[AddUsernames, Depends(get_create_usernames)],
    vendor_repository: Annotated[VendorRepository, Depends(get_vendor_repository)],
    txt_data=Depends(get_txt_file),
):
    vendor = await vendor_repository.get(id="myapp")
    return await create_usernames(users=txt_data, watch=TraderWatch.on, app=vendor)
