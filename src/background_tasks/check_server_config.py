from pydantic_settings import BaseSettings


class CheckServerConfig(BaseSettings):
    ACTIVITY_TIME: str = "activity_time"

    #class Config:
    #    env_file = ".env"
    #    extra = "allow"