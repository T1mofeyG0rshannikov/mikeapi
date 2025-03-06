from datetime import datetime, timedelta

import pytz
from sqlalchemy import func, select

from src.dependencies.dependencies import get_ticker_repository
from src.db.database import get_db
from src.db.models.models import LogOrm, TraderOrm


async def get_tickers_activity() -> None:
    async for db in get_db():
        ticker_repository = get_ticker_repository(db)
        tickers = await ticker_repository.all()
        for ticker in tickers:
            ticker_id = ticker.id

            log_count = await db.execute(select(LogOrm.price).where(LogOrm.ticker_id == ticker_id).order_by(LogOrm.id.desc()).limit(1))
            log_count = log_count.scalar()

            last_trade_price = log_count

            current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)

            last_hour_time = current_time - timedelta(hours=1)
            query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_hour_time)
            log_count = await db.execute(query)
            log_count = log_count.scalar()

            last_hour = log_count

            subquery = (
                select(LogOrm.user_id)
                .where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_hour_time)
                .distinct()
                .alias("subquery")
            )

            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            log_count = log_count.scalar()

            last_hour_traders = log_count

            last_day_time = current_time - timedelta(days=1)

            subquery = (
                select(LogOrm.user_id)
                .where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_day_time)
                .distinct()
                .alias("subquery")
            )

            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            log_count = log_count.scalar()

            last_day_traders = log_count

            log_count = await db.execute(select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_day_time))
            log_count = log_count.scalar()

            last_day = log_count

            last_our_time = current_time - timedelta(hours=24 * 7)
            log_count = await db.execute(select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time))
            log_count = log_count.scalar()

            last_week = log_count

            last_week_time = current_time - timedelta(days=7)

            subquery = (
                select(LogOrm.user_id)
                .where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_week_time)
                .distinct()
                .alias("subquery")
            )

            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            log_count = log_count.scalar()

            last_week_traders = log_count

            last_month_time = current_time - timedelta(days=30)

            log_count = await db.execute(select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_month_time))
            last_month = log_count.scalar()

            subquery = (
                select(LogOrm.user_id)
                .where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_month_time)
                .distinct()
                .alias("subquery")
            )

            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            last_month_traders = log_count.scalar()

            log_count = await db.execute(select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id))
            trades = log_count.scalar()

            subquery = select(LogOrm.user_id).where(LogOrm.ticker_id == ticker_id).distinct().alias("subquery")

            query = select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery))
            log_count = await db.execute(select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery)))
            traders = log_count.scalar()

            if ticker.currency is None:
                currency = await db.execute(select(LogOrm.currency).where(LogOrm.ticker_id == ticker_id).limit(1))
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
