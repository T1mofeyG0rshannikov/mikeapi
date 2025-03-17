import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.background_tasks.jobs import check_server, trader_activity
from src.background_tasks.trades_activity import trades_activity
from src.background_tasks.tickers_activity import get_tickers_activity


def init_scheduler() -> None:
    timezone = pytz.timezone("Europe/Moscow")
    scheduler = AsyncIOScheduler(timezone=timezone)

    scheduler.add_job(trades_activity, "cron", hour="*")
    scheduler.add_job(get_tickers_activity, "cron", hour="*")
    scheduler.add_job(check_server, "cron", minute="*")
    scheduler.add_job(trader_activity, "cron", minute="*")

    scheduler.start()
