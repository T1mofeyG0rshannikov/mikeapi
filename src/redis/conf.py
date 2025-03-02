from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "allow"
