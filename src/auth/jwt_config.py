from functools import lru_cache

from pydantic import Extra
from pydantic_settings import BaseSettings


class JwtConfig(BaseSettings):
    secret_key: str
    algorithm: str
    expires_in: int

    class Config:
        extra = Extra.allow
        env_file = ".env"


@lru_cache
def get_jwt_config() -> JwtConfig:
    return JwtConfig()
