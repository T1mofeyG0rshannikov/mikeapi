from functools import lru_cache

from pydantic import Extra
from pydantic_settings import BaseSettings


class DbConfig(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        extra = Extra.allow


@lru_cache
def get_db_config() -> DbConfig:
    return DbConfig()
