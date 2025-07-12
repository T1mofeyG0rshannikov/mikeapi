import asyncio
from datetime import datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, Response

from src.repositories.ticker_repository import TickerRepository
from src.db.models.models import UrlEnum
from src.dependencies.dependencies import (
    get_deal_repository,
    get_device,
    get_is_main_server,
    get_ping_repository,
    get_server_status,
    get_ticker_repository,
    get_trader_repository,
)
from src.entites.deal import TRADE_OPERATIONS
from src.entites.trader import TraderWatch
from src.entites.device import Device
from src.exceptions import APIServerError, InvalidCreateLogRequest
from src.user.generate_user_code import code_exists, generate_code, get_code_index
from src.repositories.deal_repository import DealRepository
from src.repositories.ping_repository import PingRepository
from src.repositories.trader_repository import TraderRepository
from src.web.schemas.common import APIResponse
from src.web.schemas.deal import CreateDealRequest

router = APIRouter(prefix="", tags=["deals"])


@router.post("/{api_url}", response_model=APIResponse, tags=["deals"])
async def create_deal(
    device: Annotated[Device, Depends(get_device)],
    data: CreateDealRequest,
    is_main_server: Annotated[bool, Depends(get_is_main_server)],
    server_status: Annotated[UrlEnum, Depends(get_server_status)],
    trader_repository: Annotated[TraderRepository, Depends(get_trader_repository)],
    ping_repository: Annotated[PingRepository, Depends(get_ping_repository)],
    ticker_repository: Annotated[TickerRepository, Depends(get_ticker_repository)],
    deal_repository: Annotated[DealRepository, Depends(get_deal_repository)],
) -> APIResponse:
    #try:
        if data.action == "ping":
            await ping_repository.create(
                app_id=device.id,
            )
            return APIResponse(
                status="ok",
            )

        if server_status == UrlEnum.failure:
            return APIResponse(status="fail")

        elif server_status == UrlEnum.error:
            raise APIServerError("ошибка сервера, попробуйте повторить позже")

        elif server_status == UrlEnum.unavailable:
            await asyncio.sleep(60)
            return Response(status=503)
        
        try:
            username, operation, ticker_name, _, price, currency, _ = data.text.split()
            ticker = await ticker_repository.get(slug=ticker_name)
            if not ticker:
                ticker = await ticker_repository.create(slug=ticker_name, currency=currency)

            price = float(price)
            username = username[0:-1]

            operation = TRADE_OPERATIONS.get(operation)

            if not operation:
                raise InvalidCreateLogRequest("Неверный формат запроса")
        except Exception as e:
            raise InvalidCreateLogRequest("Неверный формат запроса")

        user = await trader_repository.get(username)

        if not user:
            exist_codes = await trader_repository.get_codes()
            code = generate_code()
            ind = get_code_index(exist_codes, code)
            while code_exists(exist_codes, code, ind):
                code = generate_code()
                ind = get_code_index(exist_codes, code)

            user = await trader_repository.create(username=username, code=code, watch=TraderWatch.on, app_id=device.id)
        else:
            if user.watch != TraderWatch.on:
                user.watch = TraderWatch.on
                user.app_id = device.id
                user = await trader_repository.update(user)

        moscow_tz = pytz.timezone("Europe/Moscow")
        source_tz = pytz.utc
        local_time = moscow_tz.localize(datetime.strptime(data.time, "%d:%m:%Y.%H:%M:%S"))
        moscow_time = local_time.astimezone(source_tz)

        await deal_repository.create(
            app_id=device.id,
            time=moscow_time,
            main_server=is_main_server,
            user=user,
            price=price,
            currency=currency,
            operation=operation,
            ticker=ticker,
        )
        return APIResponse(
            status="ok",
        )
    #except:
    #    raise APIServerError("Что-то пошло не так")
