from src.messaging.telegram_sender.config import TelegramSenderConfig
from aiogram import Bot


class TelegramSender:
    def __init__(self, config: TelegramSenderConfig) -> None:
        self.bot = Bot(token=config.bot_token)

    async def send(self, user_id: int, message: str) -> None:    
        await self.bot.send_message(user_id, message)
        
        