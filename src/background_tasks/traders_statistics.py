from src.repositories.settings_repository import SettingsRepository
from src.repositories.log_repository import LogRepository
from src.entites.trader import StatisticPeriod, StatisticPeriodEnum, TraderWatch
from src.repositories.trader_repository import TraderRepository
from src.entites.deal import DealOperations
from collections import deque
from datetime import datetime, timedelta


class CreateTraderStatistics:
    def __init__(
        self,
        repository: TraderRepository,
        deal_repository: LogRepository,
    ) -> None:
        self.repository = repository
        self.deal_repository = deal_repository

    async def __call__(self, period: StatisticPeriod, comission: float, start_date: datetime) -> None:
        traders = await self.repository.filter(watch=TraderWatch.on)
        traders = traders[0:5]

        today = datetime.today()
        days_count = (today.date() - start_date).days

        for trader in traders:
            print(trader)
            all_deals = await self.deal_repository.filter(trader_id=trader.id, start_time=start_date)
            for i in range(0, days_count, period.days):
                end_time = today - timedelta(days=i)
                start_time = today - timedelta(days=i+period.days)
                deals = [deal for deal in all_deals if start_time <= deal.created_at <= end_time ]
                cash_balance = 0
                active_lots = {}
                deals_count = len(deals)
                trade_volume = 0
                income = 0
                
                for deal in deals:
                    active_lots[deal.ticker.slug] = active_lots.get(deal.ticker.slug, []) + [deal]
        
                    trade_volume += deal.price
                    lot = deal.ticker.lot
                    if lot is None:
                        lot = 1

                    if deal.operation == DealOperations.buy:
                        cash_balance -= (deal.price * lot) * (100 + comission) / 100                    
                    else:
                        cash_balance += (deal.price * lot) * (100 - comission) / 100
            
                cash_balance = max(0, cash_balance)
            
                stock_balance = 0
                active_lots_count = 0
                profitable_deals = 0
                unprofitable_deals = 0
                
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
                                profit = deal.price - last_deal.price - (deal.price + last_deal.price) * comission / 100
                                income += profit
                                if profit > 0:
                                    profitable_deals += 1
                                else:
                                    unprofitable_deals += 1
                            
                    stock_balance += current_price * len(que)
                    active_lots_count += len(que)

                yield_ = (2 * income / trade_volume if trade_volume != 0 else 0) * 100

                tickers_count = len(active_lots)
                gain = profitable_deals / (profitable_deals + unprofitable_deals) if (profitable_deals + unprofitable_deals) != 0 else 0

                date_value = period.date_value(today)
                await self.repository.create_statistics(
                    date=today,
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
                    tickers=tickers_count
                )


class TraderStatistics:
    def __init__(
        self, 
        settings_repository: SettingsRepository, 
        create_statistics: CreateTraderStatistics, 
        trader_repository: TraderRepository
    ) -> None:
        self.settings_repository = settings_repository
        self.create_statistics = create_statistics
        self.trader_repository = trader_repository

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
            if period.days == 1:
                await self.create_statistics(period, comission=comission, start_date=(datetime.today() - timedelta(days=1)).date())
            else:
                await self.trader_repository.delete_statistics(period=period.view)
                await self.create_statistics(period, comission=comission, start_date=start_date)