from datetime import datetime, timedelta

import pytz
from sqlalchemy import func, select

from src.db.database import Session
from src.db.models import LogActivityOrm, LogOrm


def create_log_activity(db=Session()):
    now = datetime.now(pytz.timezone("Europe/Moscow"))
    one_hour_ago = now - timedelta(hours=1)

    activity_query = select(LogActivityOrm).where(LogActivityOrm.date == now.date())
    activity = db.execute(activity_query)
    activity = activity.scalars().first()

    if not activity:
        activity = LogActivityOrm(date=now.date())

        db.add(activity)
        db.commit()

    last_hour_query = select(func.count(LogOrm.id)).where(LogOrm.time >= one_hour_ago)
    last_hour_count = db.execute(last_hour_query)
    last_hour_count = last_hour_count.scalars().first()

    attr = str(now.time().hour - 1)
    attr = "0" * (2 - len(attr)) + attr

    setattr(activity, f"hour{attr}", last_hour_count)
    activity.last_day += last_hour_count

    db.commit()
    print("log activity updated")
