from src.db.database import db_generator
import asyncio
from sqlalchemy import func

from src.db.models.models import DealOrm


async def get_active_traders_count():
    async for db in db_generator():
        print("started")
        unique_trader_count = await db.execute(func.count(DealOrm.user_id.distinct()))
        unique_trader_count = unique_trader_count.scalar()

        print(f"Количество уникальных trader_id: {unique_trader_count}") # Вывод: Количество уникальных trader_id: 2
            

if __name__ == "__main__":
    asyncio.run(get_active_traders_count())