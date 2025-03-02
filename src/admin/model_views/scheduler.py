from src.admin.forms import SchedulerForm
from src.admin.model_views.base import BaseModelView
from src.db.models.models import SchedulerRuleOrm


class SchedulerAdmin(BaseModelView, model=SchedulerRuleOrm):
    column_list = [SchedulerRuleOrm.day_l, SchedulerRuleOrm.day_r, SchedulerRuleOrm.hour_l, SchedulerRuleOrm.hour_r, SchedulerRuleOrm.interval1, SchedulerRuleOrm.interval2]

    name = "Расписание"
    name_plural = "Расписание"

    form = SchedulerForm