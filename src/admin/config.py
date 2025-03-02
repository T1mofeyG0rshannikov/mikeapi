from functools import lru_cache

from pydantic import Extra
from pydantic_settings import BaseSettings


class AdminConfig(BaseSettings):
    admin_secret_key: str
    debug: bool

    class Config:
        extra = Extra.allow
        env_file = ".env"


@lru_cache
def get_admin_config() -> AdminConfig:
    return AdminConfig()
