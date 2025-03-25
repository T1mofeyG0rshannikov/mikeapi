from pytz import timezone
from src.messaging.sms_sender.sender import SMSSender
from src.messaging.telegram_sender.sender import TelegramSender
from src.repositories.server_log_repositrory import ServerLogRepository
from src.repositories.ping_repository import PingRepository
from src.alerts_service.service import AlertsService
from src.entites.contacts import ContactChannel
from src.repositories.vendor_repository import VendorRepository
from src.entites.alert import AlertChannels
from src.repositories.log_repository import DealRepository
from src.repositories.scheduler_repository import SchedulerRepository
from datetime import datetime


class CheckServerActivity:
    def __init__(
        self, 
        repository: DealRepository, 
        scheduler_repository: SchedulerRepository, 
        vendor_repository: VendorRepository,
        telegram_sender: TelegramSender,
        sms_sender: SMSSender,
        alerts_service: AlertsService,
        ping_repository: PingRepository,
        server_log_repository: ServerLogRepository
    ) -> None:
        self.ping_repository = ping_repository
        self.sms_sender = sms_sender
        self.telegram_sender = telegram_sender
        self.repository = repository
        self.scheduler_repository = scheduler_repository
        self.vendor_repository = vendor_repository
        self.alerts_service = alerts_service
        self.server_log_repository = server_log_repository

    async def format_message(self, message: str, time) -> str:
        device = await self.vendor_repository.first()
        message = message.replace("{DEVICE}", device.app_id).replace("{TIME}", time.astimezone(timezone("Europe/Moscow")).strftime(
            "%d.%m.%Y %H:%M:%S"
        ))
        
        return message

    async def send_telegram(self, message: str, time: datetime) -> None:
        contacts = await self.scheduler_repository.get_contacts()
        message = await self.format_message(message, time)
        for contact in contacts:
            if contact.channel == ContactChannel.tg:
                await self.telegram_sender.send(contact.contact, message)
                
    async def send_sms(self, message: str, time: datetime) -> None:
        contacts = await self.scheduler_repository.get_contacts()
        message = await self.format_message(message, time)
        for contact in contacts:
            if contact.channel == ContactChannel.phone:
                await self.sms_sender.send(int(contact.contact), message)
        
    async def send_warning(self, time: datetime, first:bool=True, logs:bool=True) -> None:
        alerts = await self.scheduler_repository.alerts()

        if first:
            if logs:
                message = alerts.first_log
                channel = alerts.first_log_channel
            else:
                message = alerts.first_ping
                channel = alerts.first_ping_channel
        
        else:
            if logs:
                message = alerts.second_log
                channel = alerts.second_log_channel
            else:
                message = alerts.second_ping
                channel = alerts.second_ping_channel
                
        if channel == AlertChannels.tg:
            await self.send_telegram(message, time)

        elif channel == AlertChannels.sms:
            await self.send_sms(message, time)

        elif channel == AlertChannels.all:
            await self.send_telegram(message, time)
            await self.send_sms(message, time)
        
        message = await self.format_message(message, time)
        await self.server_log_repository.create(
            body=message
        )

    async def send_recovered(self, time, logs: bool=True) -> None:
        alerts = await self.scheduler_repository.alerts()
        if logs:
            message = alerts.trades_recovered
            channel = alerts.trades_recovered_channel
        else:
            message = alerts.pings_recovered
            channel = alerts.pings_recovered_channel
        
        if channel == AlertChannels.tg:
            await self.send_telegram(message, time)
        elif channel == AlertChannels.sms:
            await self.send_sms(message, time)
        elif channel == AlertChannels.all:
            await self.send_telegram(message, time)
            await self.send_sms(message, time)
            
        message = await self.format_message(message, time)
        await self.server_log_repository.create(
            body=message
        )

    async def check_trades(self):
        rules = await self.scheduler_repository.all()
        for rule in rules:
            time = datetime.now(timezone('Europe/Moscow')) 
            week_day = time.weekday()
            print(rule)
            print(rule.time_l <= time.time() <= rule.time_r)
            
            if week_day in rule.weekrange:
                if rule.time_l <= time.time() <= rule.time_r:
                    last_trade = await self.repository.last()
                    if last_trade is None:
                        return
                    
                    minutes_diff = (time - last_trade.created_at).total_seconds() / 60

                    time = last_trade.created_at
                    if minutes_diff > rule.interval2:
                        if not self.alerts_service.is_second_send():
                            await self.send_warning(time, first=False)
                            self.alerts_service.set_second_send(True)
                    elif minutes_diff > rule.interval1:
                        if not self.alerts_service.is_first_send():
                            await self.send_warning(time, first=True)
                            self.alerts_service.set_first_send(True)
                            await self.server_log_repository.create(
                                body=f'''Шлюз недоступен с {time.strftime("%d.%m.%Y %H:%M:%S")}'''
                            )
                    else:
                        if not self.alerts_service.is_pulled_up():
                            self.alerts_service.set_pulled_up()
                            await self.send_recovered(time, logs=True)
                            await self.server_log_repository.create(
                                body=f'''Шлюз восстановлен в {time.strftime("%d.%m.%Y %H:%M:%S")}'''
                            )


    async def check_pings(self) -> None:
        alerts = await self.scheduler_repository.alerts()
        
        time = datetime.now(timezone('Europe/Moscow'))
        
        last_ping = await self.ping_repository.last()
        if last_ping is None:
            return

        minutes_diff = (time - last_ping.created_at).total_seconds() / 60
        #minutes_diff = rule.interval1+0.5
        time = last_ping.created_at
        if minutes_diff > alerts.pings_interval2:
            if not self.alerts_service.is_second_send_ping():
                await self.send_warning(time, first=False, logs=False)
                self.alerts_service.set_second_send_ping(True)
        elif minutes_diff > alerts.pings_interval1:
            if not self.alerts_service.is_first_send_ping():
                await self.send_warning(time, first=True, logs=False)
                self.alerts_service.set_first_send_ping(True)
        else:
            if not self.alerts_service.is_pulled_up_ping():
                self.alerts_service.set_pulled_up_ping()
                await self.send_recovered(time, logs=False)
        
    async def __call__(self) -> None:
        await self.check_pings()
        await self.check_trades()
