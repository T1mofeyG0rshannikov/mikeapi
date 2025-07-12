from typing import Annotated

from fastapi import APIRouter, Depends

from src.db.get_settings import get_settings
from src.entites.device import Device
from src.db.mappers.signal import from_orm_to_signal
from src.repositories.signal_repository import SignalRepository
from src.web.schemas.signal import SignalsResponse
from src.dependencies.dependencies import get_device_get, get_signal_repository
from src.exceptions import ObjectNotFound
from src.web.validate_time import validate_time

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/", response_model=SignalsResponse, tags=["signals"])
async def get_signals(
    signal_repository: Annotated[SignalRepository, Depends(get_signal_repository)],
    device: Annotated[Device, Depends(get_device_get)],
    tickers: str | None = None,
    inds: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None
) -> SignalsResponse:
    start_time = validate_time(start_time) if start_time else None
    end_time = validate_time(end_time) if end_time else None
    tickers = tickers.split(",") if tickers else []
    inds = inds.split(",") if inds else []

    settings = get_settings()

    signals = await signal_repository.filter(limit=settings.package_max_signals, ticker_slugs=tickers, trader_ids=inds)
    signals_ids = [s.id for s in signals]
    package = await signal_repository.create_package(signal_ids=signals_ids, device_id=device.id)

    more_signals_count = await signal_repository.count(ticker_slugs=tickers, trader_ids=inds)
    more_signals_count -= len(signals_ids)

    return SignalsResponse(
        package=package.id,
        count=len(signals_ids),
        signals=[
            from_orm_to_signal(s) for s in signals
        ],
        more_signals_count=more_signals_count
    )


@router.get("/confirm/{package_id}")
async def confirm_package(
    device: Annotated[Device, Depends(get_device_get)],
    signal_repository: Annotated[SignalRepository, Depends(get_signal_repository)],
    package_id: int
):
    package = await signal_repository.get_package(id=package_id)
    if not package:
        raise ObjectNotFound

    await signal_repository.update_many(ids=package.signal_ids, adopted=True, adopted_device=package.device)
