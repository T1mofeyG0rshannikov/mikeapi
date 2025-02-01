from pydantic import BaseModel


class AppRequest(BaseModel):
    app_id: str
    auth_token: str


class APIResponse(BaseModel):
    status: str
