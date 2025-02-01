from dataclasses import dataclass


@dataclass
class Vendor:
    id: int
    app_id: str
    auth_token: str
