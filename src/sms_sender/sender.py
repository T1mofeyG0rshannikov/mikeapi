from smsaero import SmsAero
from src.sms_sender.config import SMSAeroConfig


class SMSSender:
    def __init__(self, config: SMSAeroConfig) -> None:
        self.config = config

    async def send(self, phone: int, text: str) -> None:
        api = SmsAero(self.config.sms_email, self.config.sms_api_key)

        return api.send_sms(phone, text)
