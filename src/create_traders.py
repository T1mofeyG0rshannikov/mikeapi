from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import select

from src.db.database import SessionLocal
from src.db.models.models import TraderOrm
from src.entites.trader import TraderStatus, TraderWatch
from src.generate_user_code import code_exists, generate_code, get_code_index
from src.repositories.trader_repository import TraderRepository


TRADER_PORTFOLIO = {
    "до 0": "<10K",
    "до 1": "<10K",
    "до 10000": "<10K",
    "до 50000": "10-50K",
    "до 100000": "50-100K",
    "до 500000": "100-500K",
    "до 1000000": "500K-1M",
    "до 5000000": "1-5M",
    "до 10000000": "5-10M",
    "от 10000000": "10M+",
}


class TraderCode:
    def __init__(self, code: str):
        self._code = code

    def __eq__(self, value):
        pass


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


class CreateTraders:
    def __init__(self, repository: TraderRepository) -> None:
        self.traders_repository = repository

    async def __call__(self, csvinput) -> None:
        db=SessionLocal()
        exist_codes = await self.traders_repository.get_codes()

        traders_data = []
        for row in csvinput:
            profit = float(row[6].strip().replace("−", "-"))
            status = row[1].strip() if profit != 0 else TraderStatus.unactive
            if row[1].strip() == TraderStatus.hidden:
                status = TraderStatus.hidden

            traders_data.append(
                TraderCreateDTO(
                    username=row[0].strip(),
                    status=status,
                    subscribes=int(row[2].strip()),
                    subscribers=int(row[3].strip()),
                    portfolio=TRADER_PORTFOLIO.get(row[4].strip())
                    if len(row[4].strip()) > 0
                    else None,
                    trades=int(row[5].strip()),
                    profit=profit,
                    badges=[
                        s for s in row[7].split(", ") if len(s) > 2
                    ],
                )
            )

        traders_data = sorted(set(traders_data), key=lambda t: t.username)
        traders_names = [user.username for user in traders_data]
        print(len(traders_names))
        print(len(set(traders_names)))
        traders = []
        for i in range(0, len(traders_names), 5000):
            query = select(TraderOrm).where(TraderOrm.username.in_(traders_names[i:i+5000]))
            result = await db.execute(query)
            traders.extend(result.scalars().all())
        traders = sorted(traders, key=lambda t: t.username)

        for ind, trader in enumerate(traders):
            trader.status = traders_data[ind].status
            trader.subscribes = traders_data[ind].subscribes
            trader.subscribers = traders_data[ind].subscribers
            trader.portfolio = traders_data[ind].portfolio
            trader.trades = traders_data[ind].trades
            trader.profit = traders_data[ind].profit
            trader.badges = traders_data[ind].badges

            if trader.watch == TraderWatch.pre:
                trader.last_update = datetime.utcnow()
                trader.watch = TraderWatch.new
            if trader.watch == TraderWatch.pre or trader.watch == TraderWatch.new:
                trader.app = None

        exist_trader_names = [t.username for t in traders]

        user_names = [user for user in traders_data if user.username not in exist_trader_names]

        users_to_create = []
        for user in user_names:
            code = generate_code()
            ind = get_code_index(exist_codes, code)
            while code_exists(exist_codes, code, ind):
                code = generate_code()
                ind = get_code_index(exist_codes, code)

            exist_codes.insert(ind, code)

            users_to_create.append(TraderOrm(**user.__dict__, code=code))
        db.add_all(users_to_create)
        await db.commit()
