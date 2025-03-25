from datetime import datetime, timedelta

import pytz
from sqlalchemy import func, select

from src.repositories.log_repository import DealRepository
from src.dependencies.container import Container
from src.dependencies.dependencies import get_ticker_repository
from src.db.database import get_db
from src.db.models.models import DealOrm, TraderOrm


async def get_tickers_activity() -> None:
    async for db in get_db():
        ticker_repository = get_ticker_repository(db)
        deal_repository: DealRepository = await Container.log_repository()
        tickers = await ticker_repository.all()
        for ticker in tickers:
            ticker_id = ticker.id

            last_deal = await deal_repository.last(ticker_slug=ticker.slug)

            last_trade_price = last_deal.price

            current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)

            last_hour_time = current_time - timedelta(hours=1)

            last_hour = await deal_repository.count(ticker_id=ticker.id, time_gte=last_hour_time)

            subquery = (
                select(DealOrm.user_id)
                .where(DealOrm.ticker_id == ticker_id, DealOrm.time >= last_hour_time)
                .distinct()
                .alias("subquery")
            )

            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            log_count = log_count.scalar()

            last_hour_traders = log_count

            last_day_time = current_time - timedelta(days=1)

            subquery = (
                select(DealOrm.user_id)
                .where(DealOrm.ticker_id == ticker_id, DealOrm.time >= last_day_time)
                .distinct()
                .alias("subquery")
            )

            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            log_count = log_count.scalar()

            last_day_traders = log_count

            last_day = await deal_repository.count(ticker_id=ticker.id, time_gte=last_day_time)

            last_week_time = current_time - timedelta(days=7)
            last_week = await deal_repository.count(ticker_id=ticker.id, time_gte=last_week_time)

            subquery = (
                select(DealOrm.user_id)
                .where(DealOrm.ticker_id == ticker_id, DealOrm.time >= last_week_time)
                .distinct()
                .alias("subquery")
            )

            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            log_count = log_count.scalar()

            last_week_traders = log_count

            last_month_time = current_time - timedelta(days=30)

            last_month = await deal_repository.count(ticker_id=ticker.id, time_gte=last_month_time)

            subquery = (
                select(DealOrm.user_id)
                .where(DealOrm.ticker_id == ticker_id, DealOrm.time >= last_month_time)
                .distinct()
                .alias("subquery")
            )

            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            last_month_traders = log_count.scalar()

            trades = await deal_repository.count(ticker_id=ticker.id)

            subquery = select(DealOrm.user_id).where(DealOrm.ticker_id == ticker_id).distinct().alias("subquery")

            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            traders = log_count.scalar()

            if ticker.currency is None:
                currency = await db.execute(select(DealOrm.currency).where(DealOrm.ticker_id == ticker_id).limit(1))
                currency = currency.scalar()
                ticker.currency = currency

            ticker.trades = trades
            ticker.traders = traders
            ticker.last_month_traders = last_month_traders
            ticker.last_month = last_month
            ticker.last_week_traders = last_week_traders
            ticker.last_week = last_week
            ticker.last_day = last_day
            ticker.last_day_traders = last_day_traders
            ticker.last_hour_traders = last_hour_traders
            ticker.last_hour = last_hour
            ticker.last_trade_price = last_trade_price

        print("ticker activity")
        await db.commit()
#126