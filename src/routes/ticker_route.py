from typing import Annotated

from fastapi import APIRouter, Depends

from src.schemas.ticker import ChangeTickersRequest
from src.repositories.ticker_repository import TickerRepository
from src.dependencies.dependencies import get_ticker_repository


router = APIRouter(prefix="/tickers", tags=["tickers"])


@router.post("/change", status_code=202, tags=["tickers"])
async def change_tickers(
    ticker_repository: Annotated[TickerRepository, Depends(get_ticker_repository)],
    data: ChangeTickersRequest
):
    await ticker_repository.update_many(slugs=data.ids, is_active=data.status)
