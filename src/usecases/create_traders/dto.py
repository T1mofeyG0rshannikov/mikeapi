from pydantic import BaseModel


class TraderCreateDTO(BaseModel):
    username: str
    profit: float
    status: str | None = None
    subscribes: int | None = None
    subscribers: int | None = None
    portfolio: str | None = None
    trades: int | None = None
    badges: list[str] = []
    
    def __hash__(self):
        return hash(self.username)

    def __eq__(self, other):
        return self.username == other.username

    def __gt__(self, other):
        return self.username > other.username

    def __lt__(self, other):
        return self.username < other.username