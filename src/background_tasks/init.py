import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from src.background_tasks.create_log_activity import create_log_activity
from src.background_tasks.tickers_activity import get_tickers_activity


def init_scheduler() -> None:
    timezone = pytz.timezone("Europe/Moscow")
    scheduler = BackgroundScheduler(timezone=timezone)

    scheduler.add_job(create_log_activity, "cron", hour="*")
    scheduler.add_job(get_tickers_activity, "cron", hour="*")

    scheduler.start()
