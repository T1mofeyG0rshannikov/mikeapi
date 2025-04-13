from datetime import datetime, timedelta

import pytz

from src.repositories.ticker_repository import TickerRepository
from src.repositories.settings_repository import SettingsRepository
from src.repositories.deal_repository import DealRepository


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

    def last_deal(self, deals, date, start_ind=0):
        for ind, deal in enumerate(deals[start_ind::]):
            if deal.time.date() == date:
                return deal, ind + start_ind
        return None, 0

    async def __call__(self) -> None:
        tickers = await self.ticker_repository.all()

        settings = await self.settings_repository.get()
        start_date = settings.start_date

        today = datetime.now(pytz.timezone("Europe/Moscow")).date()
        days_count = (today - start_date).days

        for ticker in tickers:
            list_range = list(range(0, days_count+1, 1))
            ticker_deals = await self.deal_repository.filter(start_time=start_date, ticker_id=ticker.id)
            ticker_deals = ticker_deals[::-1]
            ticker_price = None
            ind = 0
            for i in reversed(list_range):
                aware_date = today - timedelta(days=i)
                if ticker.slug == "RU000A10B1Q6":
                    print(aware_date)
                deal, ind = self.last_deal(ticker_deals, aware_date, ind)

                if deal:
                    price_exist = await self.ticker_repository.price_exist(ticker_id=ticker.id, date=aware_date)
                    if not price_exist:
                        ticker_price = await self.ticker_repository.create_ticker_price(
                            ticker_id=ticker.id,
                            price=deal.price,
                            date=aware_date
                        )
                    else:
                        break
                else:
                    if ticker_price:
                        price_exist = await self.ticker_repository.price_exist(ticker_id=ticker.id, date=aware_date)
                        if not price_exist:
                            ticker_price = await self.ticker_repository.create_ticker_price(
                                ticker_id=ticker.id,
                                price=ticker_price.price,
                                date=aware_date
                            )
                        else:
                            break
