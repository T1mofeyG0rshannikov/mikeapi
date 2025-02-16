from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from src.exceptions import InvalidCreateLogRequest


class CreateLogRequest(BaseModel):
    app_id: str
    auth_token: str
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
            #raise ValueError("Invalid time format. Use DD:MM:YYYY.hh:mm:ss")
