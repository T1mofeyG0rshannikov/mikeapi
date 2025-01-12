from enum import StrEnum

from src.db.models import TraderOrm
from src.generate_user_code import code_exists, generate_code, get_code_index
from src.repositories.trader_repository import TraderRepository


class TraderStatus(StrEnum):
    active = "Активный"
    hiden = "Скрытый"
    banned = "Забаненный"


class TradefBadge(StrEnum):
    verified = "Верифицирован"
    author = "Автор стратегии"
    Tchoice = "Выбор Т-Инвестиций"
    popular = "Популярный"
    helper = "Помощник пульса"


class TraderCode:
    def __init__(self, code: str):
        self._code = code

    def __eq__(self, value):
        pass


from typing import List

from pydantic import BaseModel


class TraderCreateDTO(BaseModel):
    username: str
    status: str | None = None
    subscribes: int | None = None
    subscribers: int | None = None
    portfolio: int | None = None
    trades: int | None = None
    profit: float | None = None
    badges: list[str] = []


from sqlalchemy import select

from src.db.database import SessionLocal


class CreateTraders:
    def __init__(self, repository: TraderRepository) -> None:
        self.traders_repository = repository

    async def __call__(self, csvinput, db=SessionLocal()) -> None:
        exist_codes = await self.traders_repository.get_codes()

        traders_data = []
        for row in csvinput:
            traders_data.append(
                TraderCreateDTO(
                    username=row[0].strip(),
                    status=row[1].strip(),
                    subscribes=int(row[2].strip()),
                    subscribers=int(row[3].strip()),
                    portfolio=int(row[4].strip()[3:-1].replace(" ", ""))
                    if len(row[4].strip()[3:-1].replace(" ", "")) > 0
                    else None,
                    trades=int(row[5].strip()),
                    profit=float(row[6].strip().replace("−", "-")),
                    badges=[
                        s.strip('"').strip().strip('"').strip("'")
                        for s in row[7::]
                        if len(s.strip('"').strip().strip('"')) > 0
                    ],
                )
            )

        traders_data = sorted(traders_data, key=lambda t: t.username)
        traders_names = [user.username for user in traders_data]

        query = select(TraderOrm).where(TraderOrm.username.in_(traders_names))
        result = await db.execute(query)
        traders = result.scalars().all()

        for ind, trader in enumerate(traders):
            trader.status = traders_data[ind].status
            trader.subscribes = traders_data[ind].subscribes
            trader.subscribers = traders_data[ind].subscribers
            trader.portfolio = traders_data[ind].portfolio
            trader.trades = traders_data[ind].trades
            trader.profit = traders_data[ind].profit
            trader.badges = traders_data[ind].badges

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
