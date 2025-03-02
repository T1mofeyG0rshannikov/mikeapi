from src.db.models.models import SchedulerRuleOrm
from src.entites.schedler import ScheduleRule


def from_orm_to_rule(rule: SchedulerRuleOrm) -> ScheduleRule:
    return ScheduleRule(
        day_l=rule.day_l,
        day_r=rule.day_r,
        hour_l=rule.hour_l,
        hour_r=rule.hour_r,
        minute_l=rule.minute_l,
        minute_r=rule.minute_r,
        interval1=rule.interval1,
        interval2=rule.interval2
    )
