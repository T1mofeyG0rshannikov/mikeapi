import schedule
import time
import asyncio

from src.repositories.ping_repository import PingRepository
from src.repositories.scheduler_repository import SchedulerRepository
from src.repositories.vendor_repository import VendorRepository
from src.repositories.log_repository import LogRepository
from src.background_tasks.check_server_available import CheckServerActivity
from src.db.database import SessionLocal
from src.dependencies.base_dependencies import get_alerts_service, get_sms_service, get_telegram_sender


async def job():
    db = SessionLocal()
    check_server_activity = CheckServerActivity(
        repository=LogRepository(db),
        scheduler_repository=SchedulerRepository(db), 
        vendor_repository=VendorRepository(db),
        telegram_sender=get_telegram_sender(),
        sms_sender=get_sms_service(),
        alerts_service=get_alerts_service(),
        ping_repository=PingRepository(db)
    )
    await check_server_activity()
    await db.close()

def test():
    print(time.time())
    asyncio.get_event_loop().run_until_complete(job())

schedule.every(1).minutes.do(test)

while True:
    schedule.run_pending()
    time.sleep(1)