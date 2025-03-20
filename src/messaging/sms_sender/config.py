from pydantic_settings import BaseSettings


class SMSAeroConfig(BaseSettings):
    sms_api_key: str
    sms_email: str

    class Config:
        env_file = ".env"
        extra = "allow"
