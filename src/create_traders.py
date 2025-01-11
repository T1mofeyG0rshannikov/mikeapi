from dataclasses import dataclass
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


@dataclass
class Trader:
    username: str
    status: TraderStatus
    badges: list[TradefBadge]
    code: TraderCode


class CreateTraders:
    def __init__(self, repository: TraderRepository) -> None:
        self.repository = repository

    async def __call__(self, csvinput):
        exist_codes = await self.repository.get_codes()

        traders = []

        for row in csvinput:
            code = generate_code()
            ind = get_code_index(exist_codes, code)
            while code_exists(exist_codes, code, ind):
                code = generate_code()
                ind = get_code_index(exist_codes, code)

            traders.append(
                TraderOrm(
                    username=row[0].strip(),
                    code=code,
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

            exist_codes.insert(ind, code)

        await self.repository.create_many(traders)
