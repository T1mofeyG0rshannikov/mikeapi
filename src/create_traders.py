from dataclasses import dataclass
from enum import StrEnum
from random import randrange

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import SessionLocal
from src.db.models import TraderOrm
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

    def generate_all_codes() -> str:
        codes = set()
        for a in range(65, 91):
            for b in range(10):
                for c in range(65, 91):
                    for d in range(65, 91):
                        for e in range(10):
                            for f in range(10):
                                codes.add(f"{a}{b}.{c}{d}{e}{f}")

        return codes

    def generate_code(self) -> str:
        code = ""
        code += chr(randrange(65, 91))
        code += str(randrange(10))

        code += "."

        code += chr(randrange(65, 91))
        code += chr(randrange(65, 91))

        code += str(randrange(10))
        code += str(randrange(10))

        return code

    def get_code_index(self, codes: list[str], code: str) -> int:
        from bisect import bisect_left

        return bisect_left(codes, code)

    def code_exists(self, codes: list[str], code: str, ind: int) -> bool:
        if ind < len(codes) and codes[ind] == code:
            return True

        return False

    async def __call__(self, csvinput, session: AsyncSession = SessionLocal()):
        async with session as db:
            query = select(TraderOrm.code).order_by(TraderOrm.code)
            result = await db.execute(query)
            exist_codes = list(result.scalars().all())

            traders = []

            for row in csvinput:
                code = self.generate_code()
                ind = self.get_code_index(exist_codes, code)
                while self.code_exists(exist_codes, code, ind):
                    code = self.generate_code()
                    ind = self.get_code_index(exist_codes, code)

                traders.append(
                    TraderOrm(
                        **{
                            "username": row[0].strip(),
                            "code": code,
                            "status": row[1].strip(),
                            "subscribes": int(row[2].strip()),
                            "subscribers": int(row[3].strip()),
                            "portfolio": int(row[4].strip()[3:-1].replace(" ", ""))
                            if len(row[4].strip()[3:-1].replace(" ", "")) > 0
                            else None,
                            "trades": int(row[5].strip()),
                            "profit": float(row[6].strip().replace("−", "-")),
                            "badges": [
                                s.strip('"').strip().strip('"').strip("'")
                                for s in row[7::]
                                if len(s.strip('"').strip().strip('"')) > 0
                            ],
                        }
                    )
                )

                exist_codes.insert(ind, code)

            db.add_all(traders)
            await db.commit()
