from dataclasses import dataclass


@dataclass
class Device:
    id: int
    app_id: str
    auth_token: str
