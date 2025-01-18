from datetime import datetime, timedelta

import pytz
from sqlalchemy import func, select

from src.db.database import SessionLocal
from src.db.models import LogActivityOrm, LogOrm


async def create_log_activity(db=SessionLocal()):
    now = datetime.now(pytz.timezone("Europe/Moscow"))
    one_hour_ago = now - timedelta(hours=1)

    activity_query = select(LogActivityOrm).where(LogActivityOrm.date == now.date())
    activity = await db.execute(activity_query)
    activity = activity.scalars().first()

    if not activity:
        activity = LogActivityOrm(date=now.date())

        db.add(activity)
        await db.commit()

    last_hour_query = select(func.count(LogOrm.id)).where(LogOrm.created_at >= one_hour_ago)
    last_hour_count = await db.execute(last_hour_query)
    last_hour_count = last_hour_count.scalars().first()

    setattr(activity, f"hour{now.time().hour}", last_hour_count)
    activity.last_day += last_hour_count

    await db.commit()
