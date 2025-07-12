from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.signal_repository import SignalRepository
from src.db.database import db_generator
from src.db.models.models import UrlEnum
from src.repositories.server_log_repositrory import ServerLogRepository
from src.repositories.ticker_repository import TickerRepository
from src.entites.device import Device
from src.exceptions import InvalidAuthTokenError, UrlNotFound, VendorNotFoundError
from src.repositories.deal_repository import DealRepository
from src.repositories.ping_repository import PingRepository
from src.repositories.trader_repository import TraderRepository
from src.repositories.user_repository import UserRepository
from src.repositories.vendor_repository import DeviceRepository
from src.web.schemas.common import DeviceRequest


def get_user_repository(db: AsyncSession = Depends(db_generator)) -> UserRepository:
    return UserRepository(db)


def get_ticker_repository(db: AsyncSession = Depends(db_generator)) -> TickerRepository:
    return TickerRepository(db)


def get_vendor_repository(db: AsyncSession = Depends(db_generator)) -> DeviceRepository:
    return DeviceRepository(db)


def get_deal_repository(db: AsyncSession = Depends(db_generator)) -> DealRepository:
    return DealRepository(db)


def get_signal_repository(db: AsyncSession = Depends(db_generator)) -> SignalRepository:
    return SignalRepository(db)


def get_trader_repository(db: AsyncSession = Depends(db_generator)) -> TraderRepository:
    return TraderRepository(db)


def get_ping_repository(db: Annotated[AsyncSession, Depends(db_generator)]) -> PingRepository:
    return PingRepository(db)


def get_server_log_repository(db: Annotated[AsyncSession, Depends(db_generator)]) -> ServerLogRepository:
    return ServerLogRepository(db)


async def get_is_main_server(
    api_url: str,
    vendor_repository: Annotated[DeviceRepository, Depends(get_vendor_repository)],
) -> bool:
    vendor_urls = await vendor_repository.get_api_urls()
    if api_url == vendor_urls.main_url:
        return True
    elif api_url == vendor_urls.reverse_url:
        return False

    raise UrlNotFound(f'''no url "{api_url}"''')


async def get_server_status(
    is_main_server: Annotated[bool, Depends(get_is_main_server)],
    vendor_repository: Annotated[DeviceRepository, Depends(get_vendor_repository)],
) -> UrlEnum:
    vendor_urls = await vendor_repository.get_api_urls()
    if is_main_server:
        return vendor_urls.main_url_status

    else:
        return vendor_urls.reverse_url_status


async def get_device(
    data: DeviceRequest,
    device_repository: Annotated[DeviceRepository, Depends(get_vendor_repository)],
) -> Device:
    vendor = await device_repository.get(data.app_id)
    if not vendor:
        raise VendorNotFoundError(f"нет приложения с id '{data.app_id}'")

    if vendor.auth_token != data.auth_token:
        raise InvalidAuthTokenError(f"ошибка аутентификации в приложении '{data.app_id}' - неверный токен")

    return vendor

async def get_device_get(
    app_id: str,
    auth_token: str,
    device_repository: Annotated[DeviceRepository, Depends(get_vendor_repository)],
) -> Device:
    vendor = await device_repository.get(app_id)
    if not vendor:
        raise VendorNotFoundError(f"нет приложения с id '{app_id}'")

    if vendor.auth_token != auth_token:
        raise InvalidAuthTokenError(f"ошибка аутентификации в приложении '{app_id}' - неверный токен")

    return vendor


DeviceAnnotation = Annotated[Device, Depends(get_device)]