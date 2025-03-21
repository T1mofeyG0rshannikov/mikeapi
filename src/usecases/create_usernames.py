from bisect import bisect_left, bisect_right
from datetime import datetime
from time import time

from pydantic import BaseModel

from src.repositories.vendor_repository import VendorRepository
from src.db.models.models import TraderOrm, VendorOrm
from src.entites.trader import LoadTraderAction, TraderStatus, TraderWatch
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


TRIGGERS = ["за год", "Скрытый", "Заблокирован"]


def valid_username(username: str) -> bool:
    if any(i in username for i in TRIGGERS):
        return False

    return True


class AddUsernames:
    def __init__(self, repository: TraderRepository, vendor_repository: VendorRepository) -> None:
        self.traders_repository = repository
        self.vendor_repository = vendor_repository

    def count(self, users, user) -> int:
        return bisect_right(users, user) - bisect_left(users, user)

    async def __call__(
        self,
        users: list[CreateUsernameDTO],
        watch: str = TraderWatch.pre,
        app: VendorOrm | None = None,
        action: str | None = None,
    ) -> None:
        start = time()
        exist_codes = await self.traders_repository.get_codes()

        unique_users = sorted(set(users), key=lambda t: t.username)
        unique_user_names = [user.username for user in unique_users]
        
        app = await self.vendor_repository.first()

        traders = await self.traders_repository.filter_by_usernames(unique_user_names)

        for trader in traders:
            ind = bisect_left(unique_user_names, trader.username)
            ucount = self.count(users, unique_users[ind])
            if trader.count:
                trader.count += ucount
            else:
                trader.count = ucount

            if action == LoadTraderAction.subscribes:
                trader.app_id = app.id
                if trader.watch != TraderWatch.on:
                    trader.last_update = datetime.utcnow()

                trader.watch = TraderWatch.on

        exist_trader_names = await self.traders_repository.get_usernames()

        user_names = [user for user in unique_users if user.username not in exist_trader_names]

        users_to_create = []
        for user in user_names:
            if not valid_username(user.username):
                continue

            print(user)
            code = generate_code()
            ind = get_code_index(exist_codes, code)
            while code_exists(exist_codes, code, ind):
                code = generate_code()
                ind = get_code_index(exist_codes, code)

            create_data = {"username": user.username, "code": code, "watch": watch, "app_id": app.id}
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
                    try:
                        create_data["profit"] = float(profit)
                        if float(profit) == 0.0:
                            create_data["status"] = TraderStatus.unactive
                    except ValueError:
                        pass
            else:
                create_data["status"] = (
                    user.data.split()[0] if create_data.get("profit") != 0 else TraderStatus.unactive
                )

            if "status" not in create_data:
                create_data["status"] = TraderStatus.active

            users_to_create.append(TraderOrm(**create_data, count=users.count(user)))
        
        print(len(set(user_names)))
        print(len(set([user.username for user in user_names])))
        print(len(traders))
        await self.traders_repository.create_many(users_to_create)
        print(time() - start)
