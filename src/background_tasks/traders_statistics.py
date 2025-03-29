from src.entites.ticker import TICKER_TYPES
from src.db.models.models import SettingsOrm
from src.repositories.settings_repository import SettingsRepository
from src.repositories.log_repository import DealRepository
from src.entites.trader import StatisticPeriod, StatisticPeriodEnum, TraderWatch
from src.repositories.trader_repository import TraderRepository
from src.entites.deal import DealOperations
from collections import deque
from datetime import datetime, timedelta
import pytz


def get_selected_ticker_types(
    settings: SettingsOrm
) -> list[str]:
    selected_types = []
    for ticker in TICKER_TYPES:
        if getattr(settings, f"count_{ticker['settings_set_field']}"):
            selected_types.append(ticker["value"])

    return selected_types


class CreateTraderStatistics:
    def __init__(
        self,
        repository: TraderRepository,
        deal_repository: DealRepository,
    ) -> None:
        self.repository = repository
        self.deal_repository = deal_repository

    async def __call__(
        self, 
        period: StatisticPeriod, 
        comission: float, 
        start_date: datetime,
        ticker_types: list[str]
    ) -> None:
        await self.repository.delete_statistics(period=period.view)
        traders = await self.repository.filter(watch=TraderWatch.on)
        traders = traders[0:50]

        yesterday = (datetime.now(pytz.timezone("Europe/Moscow")).date() - timedelta(days=1))
        days_count = (yesterday - start_date).days

        for trader in traders:
            last_statistics = await self.repository.last_statistics(trader_id=trader.id, period=period.view)
            await self.deal_repository.update_many(trader_id=trader.id, start_time=start_date, update_data={
                "yield_": None,
                "profit": None,
                "closed": None
            })
            all_deals = await self.deal_repository.filter(trader_id=trader.id, start_time=start_date, ticker_types=ticker_types)
            list_range = list(range(0, days_count+1, period.days))

            for i in reversed(list_range):
                aware_end_time = yesterday - timedelta(days=i)
                aware_start_time = yesterday - timedelta(days=i+period.days-1)

                period_deals = [deal for deal in all_deals if aware_start_time <= deal.created_at.date() <= aware_end_time]
                cash_balance = 0
                active_lots = {}
                period_active_lots = {}
                deals_count = len(period_deals)
                trade_volume = 0
                income = 0

                for deal in all_deals:
                    active_lots[deal.ticker.slug] = active_lots.get(deal.ticker.slug, []) + [deal]
        
                    lot = deal.ticker.lot
                    if lot is None:
                        lot = 1

                    if deal.operation == DealOperations.buy:
                        cash_balance -= (deal.price * lot) * (100 + comission) / 100                    
                    else:
                        cash_balance += (deal.price * lot) * (100 - comission) / 100

                    #deal.closed=False
                    #deal.end_deal = None
                    #await self.deal_repository.update(deal)

                for deal in period_deals:
                    period_active_lots[deal.ticker.slug] = period_active_lots.get(deal.ticker.slug, []) + [deal]
        
                    #lot = deal.ticker.lot
                    trade_volume += deal.price
                    #if lot is None:
                    #    lot = 1

                    #if deal.operation == DealOperations.buy:
                    #    cash_balance -= (deal.price * lot) * (100 + comission) / 100                    
                    #else:
                    #    cash_balance += (deal.price * lot) * (100 - comission) / 100

                cash_balance = max(0, cash_balance)

                stock_balance = 0
                active_lots_count = 0
                profitable_deals = 0
                unprofitable_deals = 0

                for ticker_slug, ticker_deals in period_active_lots.items():
                    que = deque()
                    last_ticker_deal = await self.deal_repository.last(ticker_slug=ticker_slug)
                    current_price = last_ticker_deal.price
                    
                    lot = ticker_deals[0].ticker.lot
                    lot = lot if lot else 1

                    for deal in ticker_deals:
                        if deal.operation == DealOperations.buy:
                            que.append(deal)
                        else:
                            if que:
                                last_deal = que.popleft()
                                profit = (deal.price - last_deal.price - (deal.price + last_deal.price) * comission / 100) * lot
                                income += profit
                                if profit > 0:
                                    profitable_deals += 1
                                else:
                                    unprofitable_deals += 1

                                deal.profit = profit
                                deal.yield_ = (profit / (lot * last_deal.price)) * 100
                                deal.closed = True
                                deal.end_deal = last_deal
                                await self.deal_repository.update(deal)

                    stock_balance += current_price * len(que)
                    active_lots_count += len(que)

                for ticker_slug, ticker_deals in active_lots.items():
                    que = deque()
                    last_ticker_deal = await self.deal_repository.last(ticker_slug=ticker_slug)
                    current_price = last_ticker_deal.price

                    for deal in ticker_deals:
                        if deal.operation == DealOperations.buy:
                            que.append(deal)
                        else:
                            if que:
                                last_deal = que.popleft()

                    stock_balance += current_price * len(que)
                    active_lots_count += len(que)

                yield_ = (2 * income / trade_volume if trade_volume != 0 else 0) * 100

                tickers_count = len(active_lots)
                gain = profitable_deals / (profitable_deals + unprofitable_deals) if (profitable_deals + unprofitable_deals) != 0 else 0

                date_value = period.date_value(aware_end_time)
                if last_statistics:
                    statistics = await self.repository.create_statistics(
                        start_date=aware_start_time,
                        end_date=aware_end_time,
                        date=yesterday,
                        period=period.view,
                        date_value=date_value,
                        trader_id=trader.id,
                        cash_balance=cash_balance,
                        cash_balance_degrees=cash_balance - last_statistics.cash_balance,
                        stock_balance=stock_balance * comission,
                        stock_balance_degrees=stock_balance * comission - last_statistics.stock_balance,
                        active_lots=active_lots_count,
                        active_lots_degrees=active_lots_count - last_statistics.active_lots,
                        deals=deals_count,
                        deals_degrees=deals_count - last_statistics.deals,
                        trade_volume=trade_volume,
                        trade_volume_degrees=trade_volume - last_statistics.trade_volume,
                        income=income,
                        income_degrees=income - last_statistics.income,
                        yield_=yield_,
                        yield_degrees=yield_ - last_statistics.yield_,
                        gain=gain,
                        gain_degrees=gain - last_statistics.gain,
                        tickers=tickers_count,
                        tickers_degrees=tickers_count - last_statistics.tickers
                    )
                else:
                    statistics = await self.repository.create_statistics(
                        start_date=aware_start_time,
                        end_date=aware_end_time,
                        date=yesterday,
                        period=period.view,
                        date_value=date_value,
                        trader_id=trader.id,
                        cash_balance=cash_balance,
                        stock_balance=stock_balance * comission,
                        active_lots=active_lots_count,
                        deals=deals_count,
                        trade_volume=trade_volume,
                        income=income,
                        yield_=yield_,
                        gain=gain,
                        tickers=tickers_count,
                    )

                last_statistics = statistics


class TraderStatistics:
    def __init__(
        self, 
        settings_repository: SettingsRepository,  
        trader_repository: TraderRepository,
        deal_repository: DealRepository
    ) -> None:
        self.deal_repository = deal_repository
        self.settings_repository = settings_repository
        self.create_statistics = CreateTraderStatistics(
            repository=trader_repository,
            deal_repository=deal_repository
        )

    async def __call__(self) -> None:
        periods = [
            StatisticPeriod(view=StatisticPeriodEnum.day),
            StatisticPeriod(view=StatisticPeriodEnum.week),
            StatisticPeriod(view=StatisticPeriodEnum.month),
            StatisticPeriod(view=StatisticPeriodEnum.three_months),
        ]

        settings = await self.settings_repository.get()
        comission = settings.commission
        start_date = settings.start_date

        for period in periods:
            print(period)
            await self.create_statistics(period, comission=comission, start_date=start_date)
        print("end statistics")