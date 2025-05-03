from datetime import datetime

from src.dependencies.decorator import inject_dependencies
from src.db.models.models import TraderStatisticOrm
from src.repositories.trader_repository import TraderRepository
from src.entites.trader import StatisticPeriod


@inject_dependencies
async def create_statistics(
    date: datetime,
    end_date: datetime,
    start_date: datetime,
    period: StatisticPeriod,
    trader_id: int,
    cash_balance: float,
    stock_balance: float,
    active_lots: int,
    deals: int,
    trade_volume: float,
    income: float,
    yield_: float,
    gain: float,
    tickers: int,
    repository: TraderRepository,
    last_statistics: TraderStatisticOrm = None,
) -> TraderStatisticOrm:
    date_value = period.date_value(end_date)
    if last_statistics:
        statistics = await repository.create_statistics(
            start_date=start_date,
            end_date=end_date,
            date=date,
            period=period.view,
            date_value=date_value,
            trader_id=trader_id,
            cash_balance=cash_balance + last_statistics.cash_balance,
            cash_balance_degrees=cash_balance,
            stock_balance=stock_balance,
            stock_balance_degrees=stock_balance - last_statistics.stock_balance,
            active_lots=active_lots,
            active_lots_degrees=active_lots - last_statistics.active_lots,
            deals=deals,
            deals_degrees=deals - last_statistics.deals,
            trade_volume=trade_volume,
            trade_volume_degrees=trade_volume - last_statistics.trade_volume,
            income=income,
            income_degrees=income - last_statistics.income,
            yield_=yield_,
            yield_degrees=yield_ - last_statistics.yield_,
            gain=gain,
            gain_degrees=gain - last_statistics.gain,
            tickers=tickers,
            tickers_degrees=tickers - last_statistics.tickers
        )
    else:
        statistics = await repository.create_statistics(
            start_date=start_date,
            end_date=end_date,
            date=date,
            period=period.view,
            date_value=date_value,
            trader_id=trader_id,
            cash_balance=cash_balance,
            stock_balance=stock_balance,
            active_lots=active_lots,
            deals=deals,
            trade_volume=trade_volume,
            income=income,
            yield_=yield_,
            gain=gain,
            tickers=tickers,
        )

    return statistics