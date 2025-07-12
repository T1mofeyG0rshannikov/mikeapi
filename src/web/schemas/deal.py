from datetime import datetime

from pydantic import validator

from src.web.schemas.common import DeviceRequest
from src.exceptions import InvalidCreateLogRequest


class CreateDealRequest(DeviceRequest):
    time: str | None = None
    text: str | None = "clubpravinvest: купил Т по 100 RUB (11.11.2011)"
    action: str | None = None

    @validator("time")
    def validate_time_format(cls, value):
        try:
            datetime.strptime(value, "%d:%m:%Y.%H:%M:%S")
            return value
        except ValueError:
            raise InvalidCreateLogRequest("Invalid time format. Use DD:MM:YYYY.hh:mm:ss")
