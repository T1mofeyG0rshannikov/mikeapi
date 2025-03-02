from pytz import timezone
from src.repositories.ping_repository import PingRepository
from src.alerts_service.service import AlertsService
from src.sms_sender.sender import SMSSender
from src.entites.contacts import ContactChannel
from src.repositories.vendor_repository import VendorRepository
from src.entites.alert import AlertChannels
from src.repositories.log_repository import LogRepository
from src.repositories.scheduler_repository import SchedulerRepository
from datetime import datetime, timedelta

from src.telegram_sender.sender import TelegramSender


class CheckServerActivity:
    def __init__(
        self, 
        repository: LogRepository, 
        scheduler_repository: SchedulerRepository, 
        vendor_repository: VendorRepository,
        telegram_sender: TelegramSender,
        sms_sender: SMSSender,
        alerts_service: AlertsService,
        ping_repository: PingRepository
    ) -> None:
        self.ping_repository = ping_repository
        self.sms_sender = sms_sender
        self.telegram_sender = telegram_sender
        self.repository = repository
        self.scheduler_repository = scheduler_repository
        self.vendor_repository = vendor_repository
        self.alerts_service = alerts_service

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
        
    async def send_warning(self, time: datetime, first=True, logs=True) -> None:
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

    async def send_recovered(self, time, logs=True):
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

    async def check_trades(self):
        rules = await self.scheduler_repository.all()
        for rule in rules:
            time = datetime.now(timezone('utc')) 
            week_day = time.weekday()
            print(rule)
            print(rule.time_l <= time.time() <= rule.time_r)
            
            if week_day in rule.weekrange:
                if rule.time_l <= time.time() <= rule.time_r:
                    if time.time().minute % rule.interval2 == 0:
                        time_l = time - timedelta(minutes=rule.interval2)
                        log_exists = await self.repository.exists(created_at_l=time_l, created_at_r=time)

                        if not log_exists:
                            if self.alerts_service.is_first_send():
                                if not self.alerts_service.is_second_send():

                                    await self.send_warning(time, first=False)
                                    self.alerts_service.set_second_send(True)
                        else:
                            if not self.alerts_service.is_pulled_up():
                                self.alerts_service.set_pulled_up()
                                await self.send_recovered(time, logs=True)
                                
                    elif time.time().minute % rule.interval1 == 0:
                        time_l = time - timedelta(minutes=rule.interval1)
                        log_exists = await self.repository.exists(created_at_l=time_l, created_at_r=time)

                        if not log_exists:
                            if not self.alerts_service.is_first_send():
                                await self.send_warning(time, first=True)
                                self.alerts_service.set_first_send(True)
                        else:
                            if not self.alerts_service.is_pulled_up():
                                self.alerts_service.set_pulled_up()
                                await self.send_recovered(time, logs=True)
    
    async def check_pings(self) -> None:
        alerts = await self.scheduler_repository.alerts()
        
        time = datetime.now(timezone('utc'))
        
        if time.minute % alerts.pings_interval2 == 0:
            time_l = time - timedelta(minutes=alerts.pings_interval2)
            ping_exists = await self.ping_repository.exists(created_at_l=time_l, created_at_r=time)

            if not ping_exists:
                if self.alerts_service.is_first_send_ping():
                    if not self.alerts_service.is_second_send_ping():
                        await self.send_warning(time, first=False, logs=False)
                        self.alerts_service.set_second_send_ping(True)
            else:
                if not self.alerts_service.is_pulled_up_ping():
                    self.alerts_service.set_pulled_up_ping()
                    await self.send_recovered(time, logs=False)
        
        elif time.minute % alerts.pings_interval1 == 0:
            time_l = time - timedelta(minutes=alerts.pings_interval1)
            ping_exists = await self.ping_repository.exists(created_at_l=time_l, created_at_r=time)

            if not ping_exists:
                if not self.alerts_service.is_first_send_ping():
                    await self.send_warning(time, logs=False, first=True)
                    self.alerts_service.set_first_send_ping(True)
            else:
                if not self.alerts_service.is_pulled_up_ping():
                    self.alerts_service.set_pulled_up_ping()
                    await self.send_recovered(time, logs=False)

    async def __call__(self) -> None:
        await self.check_pings()
        await self.check_trades()
