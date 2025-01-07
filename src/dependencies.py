from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt_config import JwtConfig, get_jwt_config
from src.auth.jwt_processor import JwtProcessor
from src.db.database import get_db
from src.password_hasher import PasswordHasher
from src.repositories.log_repository import LogRepository
from src.repositories.user_repository import UserRepository
from src.repositories.vendor_repository import VendorRepository


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_vendor_repository(db: AsyncSession = Depends(get_db)) -> VendorRepository:
    return VendorRepository(db)


def get_log_repository(db: AsyncSession = Depends(get_db)) -> LogRepository:
    return LogRepository(db)


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_processor(config: JwtConfig = get_jwt_config()) -> JwtProcessor:
    return JwtProcessor(config)
