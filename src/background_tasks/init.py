import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.background_tasks.jobs import check_server, deals_activity, ticker_prices, tickers_activity, trader_activity


def init_scheduler() -> None:
    timezone = pytz.timezone("Europe/Moscow")
    scheduler = AsyncIOScheduler(timezone=timezone)

    '''scheduler.add_job(deals_activity, "cron", minute="*")
    scheduler.add_job(tickers_activity, "cron", minute="*")
    scheduler.add_job(check_server, "cron", minute="*")
    scheduler.add_job(trader_activity, "cron", minute="*")
    scheduler.add_job(ticker_prices, "cron", minute="*")'''

    scheduler.start()
