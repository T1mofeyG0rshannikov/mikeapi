import csv
from io import StringIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from starlette.requests import Request

from src.auth.jwt_processor import JwtProcessor
from src.create_traders import CreateTraders
from src.db.models import UserOrm
from src.dependencies import (
    get_jwt_processor,
    get_trader_repository,
    get_user_repository,
)
from src.exceptions import NotPermittedError
from src.repositories.trader_repository import TraderRepository
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


async def get_csv_file(
    csv_file: UploadFile = File(...),
):
    contents = await csv_file.read()
    decoded_contents = contents.decode("utf-8")

    csv_file = StringIO(decoded_contents)
    csv_data = csv.reader(csv_file)

    return csv_data


def get_create_traders(traders_repository: TraderRepository = Depends(get_trader_repository)):
    return CreateTraders(traders_repository)


@router.post("/traders/")
async def add_traders(
    user: Annotated[UserOrm, Depends(get_user)],
    create_traders: Annotated[CreateTraders, Depends(get_create_traders)],
    csv_data=Depends(get_csv_file),
):
    if user and not user.is_superuser or not user:
        raise NotPermittedError("у вас нет прав для выполнения запроса")

    await create_traders(csv_data)
