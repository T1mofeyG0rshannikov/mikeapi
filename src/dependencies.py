from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_config import JwtConfig, get_jwt_config
from src.auth.jwt_processor import JwtProcessor
from src.create_traders import CreateTraders
from src.create_usernames import AddUsernames
from src.db.database import get_db
from src.password_hasher import PasswordHasher
from src.repositories.log_repository import LogRepository
from src.repositories.trader_repository import TraderRepository
from src.repositories.user_repository import UserRepository
from src.repositories.vendor_repository import VendorRepository


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_vendor_repository(db: AsyncSession = Depends(get_db)) -> VendorRepository:
    return VendorRepository(db)


def get_log_repository(db: AsyncSession = Depends(get_db)) -> LogRepository:
    return LogRepository(db)


def get_trader_repository(db: AsyncSession = Depends(get_db)) -> TraderRepository:
    return TraderRepository(db)


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_processor(config: JwtConfig = get_jwt_config()) -> JwtProcessor:
    return JwtProcessor(config)


def get_create_traders(traders_repository: TraderRepository = Depends(get_trader_repository)) -> CreateTraders:
    return CreateTraders(traders_repository)


def get_create_usernames(traders_repository: TraderRepository = Depends(get_trader_repository)) -> AddUsernames:
    return AddUsernames(traders_repository)
