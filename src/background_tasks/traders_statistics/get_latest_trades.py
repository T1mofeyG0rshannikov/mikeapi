from datetime import datetime
from typing import Annotated
from src.repositories.ticker_repository import TickerRepository
from src.dependencies.repos_container import ReposContainer
from src.dependencies.decorator import inject_dependencies
from src.db.models.models import DealOrm


@inject_dependencies
async def get_latest_trades(
    date: datetime,
    tickers_repository: Annotated[TickerRepository, ReposContainer.ticker_repository],
) -> dict[str, DealOrm]:
    prices = await tickers_repository.get_ticker_price(date=date)
    return {price.ticker.slug: price.price for price in prices}
