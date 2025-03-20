from pydantic_settings import BaseSettings


class TelegramSenderConfig(BaseSettings):
    bot_token: str
    
    class Config:
        extra = "allow"
        env_file = ".env"