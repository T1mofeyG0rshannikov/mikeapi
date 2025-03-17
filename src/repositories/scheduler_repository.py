from sqlalchemy import select

from src.entites.schedler import ScheduleRule
from src.db.mappers.schedule_rule import from_orm_to_rule
from src.db.models.models import AlertsOrm, ContactOrm, SchedulerRuleOrm
from src.repositories.base_reposiotory import BaseRepository


class SchedulerRepository(BaseRepository):
    async def all(self) -> list[ScheduleRule]:
        rules = await self.db.execute(select(SchedulerRuleOrm))
        rules = rules.scalars().all()
        return [from_orm_to_rule(rule) for rule in rules]

    async def alerts(self) -> AlertsOrm:
        alerts = await self.db.execute(select(AlertsOrm))
        return alerts.scalar()
    
    async def get_contacts(self) -> list[ContactOrm]:
        contacts = await self.db.execute(select(ContactOrm))
        return contacts.scalars().all()