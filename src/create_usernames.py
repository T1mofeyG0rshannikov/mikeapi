from bisect import bisect_left, bisect_right

from pydantic import BaseModel
from sqlalchemy import select

from src.create_traders import TraderStatus
from src.db.database import SessionLocal
from src.db.models import TraderOrm, VendorOrm
from src.generate_user_code import code_exists, generate_code, get_code_index
from src.repositories.trader_repository import TraderRepository


class CreateUsernameDTO(BaseModel):
    username: str
    data: str

    def __hash__(self):
        return hash(self.username)

    def __eq__(self, other):
        return self.username == other.username

    def __gt__(self, other):
        return self.username > other.username

    def __lt__(self, other):
        return self.username < other.username


class AddUsernames:
    def __init__(self, repository: TraderRepository) -> None:
        self.traders_repository = repository

    def count(self, users, user) -> int:
        return bisect_right(users, user) - bisect_left(users, user)

    async def __call__(
        self, users: list[CreateUsernameDTO], watch: str = "new", app: VendorOrm | None = None, db=SessionLocal()
    ) -> None:
        exist_codes = await self.traders_repository.get_codes()

        unique_users = sorted(set(users), key=lambda t: t.username)
        unique_user_names = [user.username for user in unique_users]

        query = select(TraderOrm).where(TraderOrm.username.in_(unique_user_names))
        result = await db.execute(query)
        traders = result.scalars().all()

        for trader in traders:
            ind = bisect_left(unique_user_names, trader.username)
            ucount = self.count(users, unique_users[ind])
            if trader.count:
                trader.count += ucount
            else:
                trader.count = ucount

            trader.watch = watch
            trader.app = app

        exist_trader_names = [t.username for t in traders]

        user_names = {user for user in users if user.username not in exist_trader_names}

        users_to_create = []
        for user in user_names:
            code = generate_code()
            ind = get_code_index(exist_codes, code)
            while code_exists(exist_codes, code, ind):
                code = generate_code()
                ind = get_code_index(exist_codes, code)

            create_data = {"username": user.username, "code": code, "watch": watch, "app": app}
            exist_codes.insert(ind, code)

            if "%" in user.data:
                profit = user.data.split()[0][0:-1].replace(",", ".").replace("−", "-")
                if "-" in profit:
                    if len(profit) > 1:
                        create_data["profit"] = float(profit)
                    else:
                        create_data["profit"] = 0
                        create_data["status"] = TraderStatus.unactive
                else:
                    create_data["profit"] = float(profit)
                    if float(profit) == 0.0:
                        create_data["status"] = TraderStatus.unactive

            else:
                create_data["status"] = (
                    user.data.split()[0] if create_data.get("profit") != 0 else TraderStatus.unactive
                )

            if "status" not in create_data:
                create_data["status"] = TraderStatus.active

            users_to_create.append(TraderOrm(**create_data, count=users.count(user)))
        db.add_all(users_to_create)
        await db.commit()
