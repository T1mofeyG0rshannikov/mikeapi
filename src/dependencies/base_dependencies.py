from functools import lru_cache

from src.background_tasks.check_server_config import CheckServerConfig
from src.alerts_service.config import AlertsServiceConfig
from src.alerts_service.service import AlertsService
from redis import Redis
from src.redis.conf import RedisConfig
from src.sms_sender.config import SMSAeroConfig
from src.sms_sender.sender import SMSSender
from src.auth.jwt_config import JwtConfig, get_jwt_config
from src.auth.jwt_processor import JwtProcessor
from src.password_hasher import PasswordHasher

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


@lru_cache
def get_check_server_config() -> CheckServerConfig:
    return CheckServerConfig()