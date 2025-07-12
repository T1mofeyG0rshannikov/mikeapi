import csv
from io import StringIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.dependencies.dependencies import DeviceAnnotation, get_trader_repository
from src.repositories.trader_repository import TraderRepository
from src.web.schemas.trader import ChangeTradersRequest
from src.web.routes.base import admin_required, get_user
from src.db.database import db_generator
from src.background_tasks.celery import create_traders_task, create_usernames_task
from src.db.models.models import TradersBuffer, UserOrm
from src.entites.trader import LoadTraderAction, TraderWatch


router = APIRouter(prefix="", tags=["traders"])


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


@router.delete("/clear-buffer/")
@admin_required
async def clear_buffer(
    user: Annotated[UserOrm, Depends(get_user)], request: Request, db: Annotated[AsyncSession, Depends(db_generator)]
):
    await db.execute(delete(TradersBuffer))
    await db.commit()
    request.session["buffer_size"] = 0

    return Response(status_code=200)


@router.post("/traders/change", status_code=202)
async def change_trader(
    device: DeviceAnnotation,
    data: ChangeTradersRequest,
    trader_repository: Annotated[TraderRepository, Depends(get_trader_repository)]
):
    await trader_repository.update_many(ids=data.ids, watch=data.watch)