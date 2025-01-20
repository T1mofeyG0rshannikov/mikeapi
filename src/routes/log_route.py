import asyncio
from datetime import datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, Response

from src.db.models import UrlEnum
from src.dependencies import (
    get_log_repository,
    get_trader_repository,
    get_vendor_repository,
)
from src.exceptions import APIServerError, InvalidAuthTokenError, VendorNotFoundError
from src.generate_user_code import code_exists, generate_code, get_code_index
from src.repositories.log_repository import LogRepository
from src.repositories.trader_repository import TraderRepository
from src.repositories.vendor_repository import VendorRepository
from src.schemas.log import APIResponse, CreateLogRequest

router = APIRouter(prefix="", tags=["logs"])


def get_operations():
    return {"купил": "buy", "продал": "sell"}


@router.post("/{api_url}")
async def create_log(
    api_url: str,
    data: CreateLogRequest,
    vendor_repository: Annotated[VendorRepository, Depends(get_vendor_repository)],
    trader_repository: Annotated[TraderRepository, Depends(get_trader_repository)],
    log_repository: Annotated[LogRepository, Depends(get_log_repository)],
    operations: Annotated[dict, Depends(get_operations)],
):
    vendor_urls = await vendor_repository.get_vendor_urls()
    if api_url == vendor_urls.main_url:
        if vendor_urls.main_url_status == UrlEnum.in_work:
            vendor = await vendor_repository.get(data.app_id)
            if not vendor:
                raise VendorNotFoundError(f"нет приложения с id '{data.app_id}'")

            if vendor.auth_token != data.auth_token:
                raise InvalidAuthTokenError(f"ошибка аутентификации в приложении '{data.app_id}' - неверный токен")

            try:
                username, operation, ticker_name, _, price, currency, _ = data.text.split()
                ticker = await log_repository.get_ticker(slug=ticker_name)
                if not ticker:
                    ticker = await log_repository.create_ticker(slug=ticker_name)

                price = float(price)
                username = username[0:-1]

                operation = operations.get(operation)

                if not operation:
                    return APIResponse(status="fail")
            except Exception as e:
                print(e)
                return APIResponse(status="fail")

            user = await trader_repository.get(username)

            if not user:
                exist_codes = await trader_repository.get_codes()
                code = generate_code()
                ind = get_code_index(exist_codes, code)
                while code_exists(exist_codes, code, ind):
                    code = generate_code()
                    ind = get_code_index(exist_codes, code)

                user = await trader_repository.create(username=username, code=code, watch="on", app=vendor)
            else:
                if user.watch != "on":
                    user.watch = "on"
                    user.app = vendor
                    user = await trader_repository.update(user)
                else:
                    if not user.app_id:
                        user.app = vendor
                        user = await trader_repository.update(user)

            moscow_tz = pytz.timezone("Europe/Moscow")
            source_tz = pytz.utc  # или другую временную зону, если известно
            local_time = moscow_tz.localize(datetime.strptime(data.time, "%d:%m:%Y.%H:%M:%S"))

            moscow_time = local_time.astimezone(source_tz)

            await log_repository.create(
                app=vendor,
                time=moscow_time,
                main_server=True,
                user=user,
                price=price,
                currency=currency,
                operation=operation,
                ticker=ticker,
            )

            return APIResponse(
                status="ok",
            )

        elif vendor_urls.main_url_status == UrlEnum.failure:
            return APIResponse(status="fail")

        elif vendor_urls.main_url_status == UrlEnum.error:
            raise APIServerError("ошибка сервера, попробуйте повторить позже")

        else:
            await asyncio.sleep(60)

    elif api_url == vendor_urls.reverse_url:
        if vendor_urls.reverse_url_status == UrlEnum.in_work:
            vendor = await vendor_repository.get(data.app_id)
            if not vendor:
                raise VendorNotFoundError(f"нет приложения с id '{data.app_id}'")

            if vendor.auth_token == data.auth_token:
                try:
                    username, operation, ticker_name, _, price, currency, _ = data.text.split()
                    ticker = await log_repository.get_ticker(slug=ticker_name)
                    if not ticker:
                        ticker = await log_repository.create_ticker(slug=ticker_name)

                    price = float(price)
                    username = username[0:-1]

                    operation = operations.get(operation)

                    if not operation:
                        return APIResponse(status="fail")
                except:
                    return APIResponse(status="fail")

                user = await trader_repository.get(username)

                if not user:
                    exist_codes = await trader_repository.get_codes()
                    code = generate_code()
                    ind = get_code_index(exist_codes, code)
                    while code_exists(exist_codes, code, ind):
                        code = generate_code()
                        ind = get_code_index(exist_codes, code)

                    user = await trader_repository.create(username=username, code=code, watch="on")
                else:
                    if user.watch != "on":
                        user.watch = "on"
                        user = await trader_repository.update(user)
                source_tz = pytz.utc  # или другую временную зону, если известно
                local_time = source_tz.localize(datetime.strptime(data.time, "%d:%m:%Y.%H:%M:%S"))

                # Указываем московское время
                moscow_tz = pytz.timezone("Europe/Moscow")

                # Переводим время в московскую временную зону
                moscow_time = local_time.astimezone(moscow_tz)

                await log_repository.create(
                    app=vendor,
                    time=moscow_time,
                    main_server=True,
                    user=user,
                    price=price,
                    currency=currency,
                    operation=operation,
                    ticker=ticker,
                )

                return APIResponse(
                    status="ok",
                )

            raise InvalidAuthTokenError(f"ошибка аутентификации в приложении '{data.app_id}' - неверный токен")

        elif vendor_urls.reverse_url_status == UrlEnum.failure:
            return APIResponse(status="fail")

        elif vendor_urls.reverse_url_status == UrlEnum.error:
            raise APIServerError("ошибка сервера, попробуйте повторить позже")

        else:
            await asyncio.sleep(60)

    return Response(status_code=404)
