from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.models import UrlEnum
from src.repositories.server_log_repositrory import ServerLogRepository
from src.repositories.ticker_repository import TickerRepository
from src.repositories.scheduler_repository import SchedulerRepository
from src.db.database import get_db
from src.entites.vendor import Vendor
from src.exceptions import InvalidAuthTokenError, UrlNotFound, VendorNotFoundError
from src.repositories.log_repository import LogRepository
from src.repositories.ping_repository import PingRepository
from src.repositories.trader_repository import TraderRepository
from src.repositories.user_repository import UserRepository
from src.repositories.vendor_repository import VendorRepository
from src.schemas.common import AppRequest


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_ticker_repository(db: AsyncSession = Depends(get_db)) -> TickerRepository:
    return TickerRepository(db)


def get_vendor_repository(db: AsyncSession = Depends(get_db)) -> VendorRepository:
    return VendorRepository(db)


def get_log_repository(db: AsyncSession = Depends(get_db)) -> LogRepository:
    return LogRepository(db)


def get_trader_repository(db: AsyncSession = Depends(get_db)) -> TraderRepository:
    return TraderRepository(db)


def get_ping_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> PingRepository:
    return PingRepository(db)


def get_server_log_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> ServerLogRepository:
    return ServerLogRepository(db)


async def get_is_main_server(
    api_url: str,
    vendor_repository: Annotated[VendorRepository, Depends(get_vendor_repository)],
) -> bool:
    vendor_urls = await vendor_repository.get_api_urls()
    if api_url == vendor_urls.main_url:
        return True
    elif api_url == vendor_urls.reverse_url:
        return False

    raise UrlNotFound(f'''no url "{api_url}"''')


async def get_server_status(
    is_main_server: Annotated[bool, Depends(get_is_main_server)],
    vendor_repository: Annotated[VendorRepository, Depends(get_vendor_repository)],
) -> UrlEnum:
    vendor_urls = await vendor_repository.get_api_urls()
    if is_main_server:
        return vendor_urls.main_url_status

    else:
        return vendor_urls.reverse_url_status


async def get_app(
    data: AppRequest,
    vendor_repository: Annotated[VendorRepository, Depends(get_vendor_repository)],
) -> Vendor:
    vendor = await vendor_repository.get(data.app_id)
    if not vendor:
        raise VendorNotFoundError(f"нет приложения с id '{data.app_id}'")

    if vendor.auth_token != data.auth_token:
        raise InvalidAuthTokenError(f"ошибка аутентификации в приложении '{data.app_id}' - неверный токен")

    return vendor
