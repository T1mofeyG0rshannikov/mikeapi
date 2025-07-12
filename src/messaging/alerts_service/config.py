from pydantic_settings import BaseSettings


class AlertsServiceConfig(BaseSettings):
    FIRST_SEND: str = "first_send"
    SECOND_SEND: str = "second_send"
    PULLED_UP: str = "pulled_up"
    
    
    FIRST_SEND_PINGS: str = "first_send_pings"
    SECOND_SEND_PINGS: str = "second_send_pings"
    PULLED_UP_PINGS: str = "pulled_up_pings"

    class Config:
        env_file = ".env"
        extra = "allow"