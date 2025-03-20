from src.admin.forms import SchedulerForm
from src.admin.model_views.base import BaseModelView
from src.db.models.models import SchedulerRuleOrm


class SchedulerAdmin(BaseModelView, model=SchedulerRuleOrm):
    column_list = [SchedulerRuleOrm.day_l, SchedulerRuleOrm.hour_l, SchedulerRuleOrm.interval1, SchedulerRuleOrm.interval2]

    name = "Расписание торгов"
    name_plural = "Расписание торгов"

    form = SchedulerForm
    
    column_formatters = {
        SchedulerRuleOrm.day_l: lambda rule, _: f"{rule.day_l}-{rule.day_r}",
        SchedulerRuleOrm.hour_l: lambda rule, _: f"{rule.hour_l}:{str(rule.minute_l).zfill(2)}-{rule.hour_r}:{str(rule.minute_r).zfill(2)}",
    }
