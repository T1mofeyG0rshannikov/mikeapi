from datetime import datetime, timedelta
import pytz
from src.db.database import get_db
from sqlalchemy import select, func
from src.db.models.models import LogOrm
import asyncio


async def trades_activity_test() -> None:
    async for db in get_db():
        now = datetime.now()
        year = now.year
        # Создаем datetime объект для 9 марта в 1:00 ночи (пока без часового пояса)
        msk_dt = datetime(year, 3, 9, 1, 0, 0)

        # Определяем московский часовой пояс
        msk_timezone = pytz.timezone('Europe/Moscow')

        # Локализуем datetime объект для московского времени
        msk_dt_localized = msk_timezone.localize(msk_dt)

        # Преобразуем в UTC
        utc_dt = msk_dt_localized.astimezone(pytz.utc)
        print(utc_dt)
        utc_dt_plus_hour = utc_dt + timedelta(hours=1)

        last_hour_count = await db.execute(select(func.count(LogOrm.id)).where(LogOrm.time >= utc_dt, LogOrm.time <= utc_dt_plus_hour))
        last_hour_count = last_hour_count.scalar_one()
        print(last_hour_count)
        

if __name__ == "__main__":
    asyncio.run(trades_activity_test())