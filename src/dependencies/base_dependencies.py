from functools import lru_cache

from src.admin.config import AdminConfig
from src.background_tasks.check_server_config import CheckServerConfig
from redis import Redis
from src.redis.conf import RedisConfig
from src.auth.jwt_config import JwtConfig
from src.auth.jwt_processor import JwtProcessor
from src.password_hasher import PasswordHasher


@lru_cache
def get_jwt_config() -> JwtConfig:
    return JwtConfig()


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_processor(config: JwtConfig = get_jwt_config()) -> JwtProcessor:
    return JwtProcessor(config)


def get_redis_config() -> RedisConfig:
    return RedisConfig()


def get_redis(conf: RedisConfig = get_redis_config()) -> Redis:
    return Redis(host="localhost", port=6379, db=0, decode_responses=True)


@lru_cache
def get_check_server_config() -> CheckServerConfig:
    return CheckServerConfig()


@lru_cache
def get_admin_config() -> AdminConfig:
    return AdminConfig()