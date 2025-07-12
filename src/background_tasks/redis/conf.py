from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):
    host: str
    port: int
    db: int

    class Config:
        env_file = ".env"
        extra = "allow"
