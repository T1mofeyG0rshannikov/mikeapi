from datetime import datetime, timedelta

import pytz
from sqlalchemy import func, select

from src.db.database import get_db
from src.db.models.models import LogActivityOrm, LogOrm


async def create_log_activity() -> None:
    print(datetime.now())
    async for db in get_db():
        now = datetime.now(pytz.timezone("Europe/Moscow"))
        one_hour_ago = now - timedelta(hours=1)

        activity = await db.execute(select(LogActivityOrm).where(LogActivityOrm.date == one_hour_ago.date()).limit(1))
        activity = activity.scalar()

        if not activity:
            activity = LogActivityOrm(date=one_hour_ago.date())

            db.add(activity)
            await db.commit()

        last_hour_count = await db.execute(select(func.count(LogOrm.id)).where(LogOrm.time >= one_hour_ago))
        last_hour_count = last_hour_count.scalar()

        attr = str(now.time().hour - 1)
        if attr == "-1":
            attr = "23"

        attr = attr.zfill(2)

        setattr(activity, f"hour{attr}", last_hour_count)
        activity.last_day += last_hour_count

        await db.commit()
