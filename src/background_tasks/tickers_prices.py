from datetime import datetime, timedelta

import pytz

from src.repositories.ticker_repository import TickerRepository
from src.repositories.settings_repository import SettingsRepository
from src.repositories.log_repository import DealRepository


class GetTickersPrices:
    def __init__(
        self, 
        deal_repository: DealRepository, 
        settings_repository: SettingsRepository,
        ticker_repositpry: TickerRepository
    ) -> None:
        self.deal_repository = deal_repository
        self.settings_repository = settings_repository
        self.ticker_repository = ticker_repositpry

    async def __call__(self) -> None:
        tickers = await self.ticker_repository.all()

        settings = await self.settings_repository.get()
        start_date = settings.start_date

        today = datetime.now(pytz.timezone("Europe/Moscow")).date()
        days_count = (today - start_date).days

        for ticker in tickers:
            list_range = list(range(0, days_count+1, 1))
            ticker_price = None
    
            for i in reversed(list_range):
                aware_date = today - timedelta(days=i)
                deal = await self.deal_repository.last(date=aware_date, ticker_slug=ticker.slug)
                if deal:
                    ticker_price = await self.ticker_repository.create_ticker_price(
                        ticker_id=ticker.id,
                        price=deal.price,
                        date=aware_date
                    )
                else:
                    ticker_price = await self.ticker_repository.create_ticker_price(
                        ticker_id=ticker.id,
                        price=ticker_price.price,
                        date=aware_date
                    )