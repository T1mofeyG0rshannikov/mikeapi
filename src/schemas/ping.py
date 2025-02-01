from pydantic import BaseModel


class CreatePingRequest(BaseModel):
    action: str
