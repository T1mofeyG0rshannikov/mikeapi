from pydantic import BaseModel, validator
from datetime import datetime
from typing import List

from src.web.schemas.common import DeviceRequest
from src.exceptions import InvalidCreateLogRequest


class SignalsResponse(BaseModel):
    package: int
    count: int
    signals: List[str]
    more_signals_count: int


class GetSignalsRequest(DeviceRequest):
    tickers: List[str] | None = None
    inds: List[str] | None = None
    start_time: str | None = None
    end_time: str | None = None

    @validator("start_time", "end_time")
    def validate_time_format(cls, value):
        try:
            datetime.strptime(value, "%d:%m:%Y.%H:%M:%S")
            return value
        except ValueError:
            raise InvalidCreateLogRequest("Invalid time format. Use DD:MM:YYYY.hh:mm:ss")
