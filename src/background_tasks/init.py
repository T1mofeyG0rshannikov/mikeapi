import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.background_tasks.check_server_job import check_server
from src.background_tasks.trades_activity import trades_activity
from src.background_tasks.tickers_activity import get_tickers_activity


def init_scheduler() -> None:
    timezone = pytz.timezone("Europe/Moscow")
    scheduler = AsyncIOScheduler(timezone=timezone)

    scheduler.add_job(trades_activity, "cron", hour="*")
    scheduler.add_job(get_tickers_activity, "cron", hour="*")
    scheduler.add_job(check_server, "cron", minute="*")

    scheduler.start()
