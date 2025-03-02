from src.db.db_config import DbConfig
from functools import lru_cache


@lru_cache
def get_db_config() -> DbConfig:
    return DbConfig()
