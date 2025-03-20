from smsaero import SmsAero
from src.messaging.sms_sender.config import SMSAeroConfig


class SMSSender:
    def __init__(self, config: SMSAeroConfig) -> None:
        self.api = SmsAero(config.sms_email, config.sms_api_key)

    async def send(self, phone: int, text: str) -> None:
        return self.api.send_sms(phone, text)
