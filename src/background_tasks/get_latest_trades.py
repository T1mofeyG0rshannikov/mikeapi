from typing import Annotated
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from src.dependencies.repos_container import ReposContainer
from src.dependencies.decorator import inject_dependencies
from src.db.models.models import DealOrm
from sqlalchemy.ext.asyncio import AsyncSession


@inject_dependencies
async def get_latest_trades(
    db: Annotated[AsyncSession, ReposContainer.db]
) -> dict[str, DealOrm]:
    subquery = (
        select(DealOrm.ticker_id, func.max(DealOrm.time).label('latest_timestamp'))
        .group_by(DealOrm.ticker_id)
        .subquery()
    )

    latest_trades_query = (
        select(DealOrm)
        .join(subquery, (DealOrm.ticker_id == subquery.c.ticker_id) & (DealOrm.time == subquery.c.latest_timestamp))
    )

    latest_trades = await db.execute(latest_trades_query.options(joinedload(DealOrm.ticker)))
    latest_trades = latest_trades.scalars().all()

    result_dict = {trade.ticker.slug: trade for trade in latest_trades}
    return result_dict
