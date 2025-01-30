from datetime import datetime, timedelta

import pytz
from sqlalchemy import func, select

from src.db.database import Session
from src.db.models import LogOrm, TickerOrm, TraderOrm


def get_tickers_activity(db=Session()) -> None:
    tickers = db.execute(select(TickerOrm)).scalars().all()
    for ticker in tickers:
        ticker_id = ticker.id
        query = select(LogOrm.price).where(LogOrm.ticker_id == ticker_id).order_by(LogOrm.id.desc())
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        last_trade_price = log_count

        current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)

        last_hour_time = current_time - timedelta(hours=1)
        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_hour_time)
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        last_hour = log_count

        subquery = (
            select(LogOrm.user_id)
            .where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_hour_time)
            .distinct()
            .alias("subquery")
        )
        query = select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery))

        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        last_hour_traders = log_count

        last_day_time = current_time - timedelta(days=1)

        subquery = (
            select(LogOrm.user_id)
            .where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_day_time)
            .distinct()
            .alias("subquery")
        )

        query = select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery))

        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        last_day_traders = log_count

        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_day_time)
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        last_day = log_count

        last_our_time = current_time - timedelta(hours=24 * 7)
        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time)
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        last_week = log_count

        last_week_time = current_time - timedelta(days=7)

        subquery = (
            select(LogOrm.user_id)
            .where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_week_time)
            .distinct()
            .alias("subquery")
        )

        query = select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery))

        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        last_week_traders = log_count

        last_month_time = current_time - timedelta(days=30)

        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_month_time)
        log_count = db.execute(query)
        last_month = log_count.scalars().first()

        subquery = (
            select(LogOrm.user_id)
            .where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_month_time)
            .distinct()
            .alias("subquery")
        )

        query = select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery))

        log_count = db.execute(query)
        last_month_traders = log_count.scalars().first()

        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id)
        log_count = db.execute(query)
        trades = log_count.scalars().first()

        subquery = select(LogOrm.user_id).where(LogOrm.ticker_id == ticker_id).distinct().alias("subquery")

        query = select(func.count(TraderOrm.id)).where(TraderOrm.id.in_(subquery))
        log_count = db.execute(query)
        traders = log_count.scalars().first()

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

    # print("ticker activity")
    db.commit()
