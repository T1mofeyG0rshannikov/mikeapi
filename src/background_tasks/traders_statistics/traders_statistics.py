from src.background_tasks.traders_statistics.create_statistics import create_statistics
from src.background_tasks.traders_statistics.get_latest_trades import get_latest_trades
from src.entites.ticker import TICKER_TYPES
from src.db.models.models import DealOrm, SettingsOrm
from src.repositories.settings_repository import SettingsRepository
from src.repositories.log_repository import DealRepository
from src.entites.trader import StatisticPeriod, StatisticPeriodEnum, TraderWatch
from src.repositories.trader_repository import TraderRepository
from src.entites.deal import DealOperations
from collections import deque
from datetime import datetime, timedelta
import pytz
from collections import defaultdict


def get_selected_ticker_types(
    settings: SettingsOrm
) -> list[str]:
    selected_types = []
    for ticker in TICKER_TYPES:
        if getattr(settings, f"count_{ticker['settings_set_field']}"):
            selected_types.append(ticker["value"])

    return selected_types


def count_profit(deal1: DealOrm, deal2: DealOrm, commission, lot) -> float:
    if deal1.operation == DealOperations.buy:
        return (deal2.price - deal1.price - (deal1.price + deal2.price) * commission / 100) * lot
    return (deal1.price - deal2.price - (deal1.price + deal2.price) * commission / 100) * lot

class CreateTraderStatistics:
    def __init__(
        self,
        repository: TraderRepository,
        deal_repository: DealRepository,
        settings_repository: SettingsRepository
    ) -> None:
        self.repository = repository
        self.deal_repository = deal_repository
        self.settings_repository = settings_repository

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

        ticker_types = get_selected_ticker_types(settings)   

        traders = await self.repository.filter(watch=TraderWatch.on)
        traders = traders[0:50]

        yesterday = (datetime.now(pytz.timezone("Europe/Moscow")).date() - timedelta(days=1))
        days_count = (yesterday - start_date).days
        #start = time.time()
        #await self.deal_repository.update_many(start_time=start_date, update_data={
        #    "yield_": None,
        #    "profit": None,
        #    "closed": None
        #})
        #print(time.time() - start)

        for period in periods:
            await self.repository.delete_statistics(period=period.view)

        last_ticker_deals = await get_latest_trades(yesterday)
        ticker_slugs = list(last_ticker_deals.keys())
        
        for trader in traders:
            all_deals = await self.deal_repository.filter(trader_id=trader.id, start_time=start_date, ticker_types=ticker_types)
            active_lots = defaultdict(list)

            for deal in all_deals:
                active_lots[deal.ticker.slug].append(deal)

            for ticker_slug, ticker_deals in active_lots.items():
                que = deque()
                lot = ticker_deals[0].ticker_lot

                for deal in ticker_deals:
                    if not que:
                        que.append(deal)
                        continue

                    if deal.operation == que[0].operation:
                        que.append(deal)
                    else:
                        last_deal = que.popleft()
                        profit = count_profit(deal1=deal, deal2=last_deal, commission=comission, lot=lot)

                        deal.profit = profit
                        deal.yield_ = (profit / (lot * last_deal.price)) * 100
                        deal.closed = True
                        deal.end_deal = last_deal
                        await self.deal_repository.update(deal)

            for period in periods:
                last_statistics = None
                list_range = list(range(0, days_count+1, period.days))
                period_deals_ques = defaultdict(deque)

                for i in reversed(list_range):
                    aware_end_time = yesterday - timedelta(days=i)
                    aware_start_time = yesterday - timedelta(days=i+period.days-1)

                    period_deals = [deal for deal in all_deals if aware_start_time <= deal.created_at.date() <= aware_end_time]

                    period_active_lots = defaultdict(list)
                    deals_count = len(period_deals)
                    trade_volume = 0
                    income = 0
                    cash_balance = 0
                    stock_balance = 0
                    active_lots_count = 0
                    profitable_deals = 0
                    unprofitable_deals = 0
                    closed_by_period_sum = 0

                    for deal in period_deals:
                        lot = deal.ticker_lot

                        period_active_lots[deal.ticker.slug].append(deal)
                        trade_volume += deal.price * lot

                        if deal.operation == DealOperations.buy:
                            cash_balance -= (deal.price * lot) * (100 + comission) / 100                    
                        else:
                            cash_balance += (deal.price * lot) * (100 - comission) / 100

                        if deal.closed:
                            closed_by_period_sum += deal.end_deal.price * lot

                    tickers_count = len(period_active_lots)

                    for ticker_slug_period in ticker_slugs:
                        ticker_deals = period_active_lots[ticker_slug_period]
                        que = period_deals_ques[ticker_slug_period]
                        last_ticker_deal = last_ticker_deals[ticker_slug_period]

                        if ticker_deals:
                            lot = ticker_deals[0].ticker_lot

                            for deal in ticker_deals:
                                if not que:
                                    que.append(deal)
                                    continue

                                if deal.operation == que[0].operation:
                                    que.append(deal)
                                else:
                                    last_deal = que.popleft()
                                    profit = count_profit(deal, last_deal, comission, lot)
                                    income += profit
                                    if profit > 0:
                                        profitable_deals += 1
                                    else:
                                        unprofitable_deals += 1

                        period_deals_ques[ticker_slug_period] = que
                        if que:
                            lot = que[0].ticker_lot
                            count = len([d for d in que if d.operation == DealOperations.buy])
                            stock_balance += last_ticker_deal * count * lot
                            active_lots_count += count

                    stock_balance = stock_balance * (100 - comission) / 100
                    yield_ = (income / closed_by_period_sum if closed_by_period_sum != 0 else 0) * 100

                    gain = (profitable_deals / (profitable_deals + unprofitable_deals) if (profitable_deals + unprofitable_deals) != 0 else 0) * 100

                    last_statistics = await create_statistics(
                        start_date=aware_start_time,
                        end_date=aware_end_time,
                        date=yesterday,
                        period=period,
                        trader_id=trader.id,
                        cash_balance=cash_balance,
                        stock_balance=stock_balance,
                        active_lots=active_lots_count,
                        deals=deals_count,
                        trade_volume=trade_volume,
                        income=income,
                        yield_=yield_,
                        gain=gain,
                        tickers=tickers_count,
                        last_statistics=last_statistics
                    )

        print("end statistics")
