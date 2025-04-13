from datetime import datetime, timedelta

import pytz

from src.repositories.deal_repository import DealRepository
from src.db.models.models import LogActivityOrm


class DealsActivity:
    def __init__(self, deal_repository: DealRepository) -> None:
        self.deal_repository = deal_repository

    async def get_activity(self, date: datetime) -> LogActivityOrm:
        activity = await self.deal_repository.get_activity(date=date)

        if not activity:
            activity = await self.deal_repository.create_activity(date=date)
        return activity

    async def __call__(self) -> None:
        now_msc = datetime.now(pytz.timezone("Europe/Moscow"))
        now_utc = datetime.now(pytz.utc)
        one_hour_ago_utc = now_utc - timedelta(hours=1)
        one_hour_ago_msc = now_msc - timedelta(hours=1)

        activity = await self.get_activity(date=one_hour_ago_msc.date())

        last_hour_count = await self.deal_repository.count(time_gte=one_hour_ago_utc)

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

        await self.deal_repository.update(activity)
