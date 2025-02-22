from datetime import datetime
from sqlalchemy import select

from src.create_traders.traders_from_csv import traders_data_from_csv
from src.db.database import SessionLocal
from src.db.models.models import TraderOrm
from src.entites.trader import TraderWatch
from src.generate_user_code import code_exists, generate_code, get_code_index
from src.repositories.trader_repository import TraderRepository


class CreateTraders:
    def __init__(self, repository: TraderRepository) -> None:
        self.traders_repository = repository

    async def __call__(self, csv_data: list[str]) -> None:
        db=SessionLocal()
        exist_codes = await self.traders_repository.get_codes()

        traders_data = traders_data_from_csv(csv_data)
        traders_names = [user.username for user in traders_data]
        print(len(traders_names))

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
