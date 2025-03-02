from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.ping_repository import PingRepository
from src.alerts_service.config import AlertsServiceConfig
from src.alerts_service.service import AlertsService
from redis import Redis
from src.redis.conf import RedisConfig
from src.repositories.user_repository import UserRepository
from src.repositories.scheduler_repository import SchedulerRepository
from src.background_tasks.check_server_available import CheckServerActivity
from src.sms_sender.config import SMSAeroConfig
from src.sms_sender.sender import SMSSender
from src.auth.jwt_config import JwtConfig, get_jwt_config
from src.auth.jwt_processor import JwtProcessor
from src.db.database import SessionLocal, get_db
from src.password_hasher import PasswordHasher
from src.repositories.log_repository import LogRepository
from src.repositories.vendor_repository import VendorRepository

from src.telegram_sender.config import TelegramSenderConfig
from src.telegram_sender.sender import TelegramSender


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_processor(config: JwtConfig = get_jwt_config()) -> JwtProcessor:
    return JwtProcessor(config)


@lru_cache
def get_sms_config() -> SMSAeroConfig:
    return SMSAeroConfig()


def get_sms_service(config: SMSAeroConfig = get_sms_config()) -> SMSSender:
    return SMSSender(config)


async def get_scheduler_repository():
    db = SessionLocal()
    try:
        return SchedulerRepository(db)
    finally:
        db.close()


async def get_log_repository():
    db = SessionLocal()
    try:
        return LogRepository(db)
    finally:
        db.close()


async def get_vendor_repository():
    db = SessionLocal()
    try:
        return VendorRepository(db)
    finally:
        db.close()

async def get_ping_repository():
    db = SessionLocal()
    try:
        return PingRepository(db)
    finally:
        db.close()

@lru_cache
def get_telegram_config():
    return TelegramSenderConfig()


def get_telegram_sender(tg_config: TelegramSenderConfig = get_telegram_config()):
    return TelegramSender(tg_config)


def get_redis_config() -> RedisConfig:
    return RedisConfig()


def get_redis(conf: RedisConfig = get_redis_config()) -> Redis:
    return Redis(host="localhost", port=6379, db=0, decode_responses=True)


@lru_cache
def get_alerts_config():
    return AlertsServiceConfig()


def get_alerts_service(redis: Redis = get_redis(), alerts_config: AlertsServiceConfig = get_alerts_config()) -> AlertsService:
    return AlertsService(redis, conf=alerts_config)


async def get_check_server_usecase() -> CheckServerActivity:
    log_repository = await get_log_repository()
    scheduler_repository = await get_scheduler_repository()
    vendor_repository = await get_vendor_repository()
    telegram_sender = get_telegram_sender()
    sms_sender = get_sms_service()
    alerts_service = get_alerts_service()
    ping_repository = await get_ping_repository()

    return CheckServerActivity(
        repository=log_repository,
        scheduler_repository=scheduler_repository, 
        vendor_repository=vendor_repository,
        telegram_sender=telegram_sender,
        sms_sender=sms_sender,
        alerts_service=alerts_service,
        ping_repository=ping_repository
    )


def get_user_repository(db: AsyncSession = SessionLocal()) -> UserRepository:
    return UserRepository(db)
