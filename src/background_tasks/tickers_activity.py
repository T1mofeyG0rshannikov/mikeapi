from datetime import datetime, timedelta

import pytz

from src.repositories.ticker_repository import TickerRepository
from src.repositories.trader_repository import TraderRepository
from src.repositories.deal_repository import DealRepository


class TickersActivity:
    def __init__(
        self, 
        ticker_repository: TickerRepository, 
        deal_repository: DealRepository, 
        trader_repository: TraderRepository
    ) -> None:
        self.deal_repository = deal_repository
        self.ticker_repository = ticker_repository
        self.trader_repository = trader_repository

    async def __call__(self) -> None:
        tickers = await self.ticker_repository.all()
        for ticker in tickers:
            last_deal = await self.deal_repository.last(ticker_id=ticker.id)

            current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)

            last_hour_time = current_time - timedelta(hours=1)
            last_day_time = current_time - timedelta(days=1)
            last_week_time = current_time - timedelta(days=7)
            last_month_time = current_time - timedelta(days=30)

            ticker.currency = last_deal.currency
            ticker.trades = await self.deal_repository.count(ticker_id=ticker.id)
            ticker.traders = await self.trader_repository.count(ticker_id=ticker.id)
            ticker.last_month_traders = await self.trader_repository.count(ticker_id=ticker.id, time_gte=last_month_time)
            ticker.last_month = await self.deal_repository.count(ticker_id=ticker.id, time_gte=last_month_time)
            ticker.last_week_traders = await self.trader_repository.count(ticker_id=ticker.id, time_gte=last_week_time)
            ticker.last_week = await self.deal_repository.count(ticker_id=ticker.id, time_gte=last_week_time)
            ticker.last_day = await self.deal_repository.count(ticker_id=ticker.id, time_gte=last_day_time)
            ticker.last_day_traders = await self.trader_repository.count(ticker_id=ticker.id, time_gte=last_day_time)
            ticker.last_hour_traders = await self.trader_repository.count(ticker_id=ticker.id, time_gte=last_hour_time)
            ticker.last_hour = await self.deal_repository.count(ticker_id=ticker.id, time_gte=last_hour_time)
            ticker.last_trade_price = last_deal.price
            await self.ticker_repository.update(ticker)

        print("ticker activity")
