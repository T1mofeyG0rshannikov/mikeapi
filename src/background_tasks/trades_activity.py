from datetime import datetime, timedelta

import pytz
from sqlalchemy import func, select

from src.db.database import get_db
from src.db.models.models import LogActivityOrm, LogOrm


async def trades_activity() -> None:
    async for db in get_db():
        now_msc = datetime.now(pytz.timezone("Europe/Moscow"))
        now_utc = datetime.now(pytz.utc)
        one_hour_ago_utc = now_utc - timedelta(hours=1)
        one_hour_ago_msc = now_msc - timedelta(hours=1)

        activity = await db.execute(select(LogActivityOrm).where(LogActivityOrm.date == one_hour_ago_msc.date()).limit(1))
        activity = activity.scalar()

        if not activity:
            activity = LogActivityOrm(date=one_hour_ago_msc.date())

            db.add(activity)
            await db.commit()

        last_hour_count = await db.execute(select(func.count(LogOrm.id)).where(LogOrm.time >= one_hour_ago_utc))
        last_hour_count = last_hour_count.scalar_one()

        attr = str(now_msc.hour - 1)
        if attr == "-1":
            attr = "23"

        attr = attr.zfill(2)

        setattr(activity, f"hour{attr}", last_hour_count)
        activity.last_day += last_hour_count
        print("-----activity-----")
        print(one_hour_ago_msc)
        print(one_hour_ago_utc)
        print(last_hour_count)
        print("-----activity-----")

        await db.commit()
