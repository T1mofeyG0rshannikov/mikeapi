from datetime import datetime

from src.db.models.models import TraderOrm
from src.entites.trader import TraderWatch
from src.user.generate_user_code import code_exists, generate_code, get_code_index
from src.repositories.trader_repository import TraderRepository
from src.usecases.create_traders.traders_from_csv import traders_data_from_csv


class CreateTraders:
    def __init__(self, repository: TraderRepository) -> None:
        self.traders_repository = repository

    async def __call__(self, csv_data: list[str]) -> None:
        exist_codes = await self.traders_repository.get_codes()

        traders_data = traders_data_from_csv(csv_data)
        traders_names = [user.username for user in traders_data]
        print(len(traders_names))

        traders = await self.traders_repository.filter_by_usernames(traders_names)
        traders = sorted(traders, key=lambda t: t.username)

        for trader_data, trader in zip(traders_data, traders):
            trader.status = trader_data.status
            trader.subscribes = trader_data.subscribes
            trader.subscribers = trader_data.subscribers
            trader.portfolio = trader_data.portfolio
            trader.trades = trader_data.trades
            trader.profit = trader_data.profit
            trader.badges = trader_data.badges

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
        await self.traders_repository.create_many(users_to_create)
