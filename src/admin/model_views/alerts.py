from src.admin.forms import AlertsForm
from src.admin.model_views.base import BaseModelView
from src.db.models.models import AlertsOrm


class AlertsAdmin(BaseModelView, model=AlertsOrm):
    column_list = [
        AlertsOrm.first_log,
        AlertsOrm.first_log_channel,
        
        AlertsOrm.second_log,
        AlertsOrm.second_log_channel,
        
        AlertsOrm.first_ping,
        AlertsOrm.first_ping_channel,
        
        AlertsOrm.second_ping,
        AlertsOrm.second_ping_channel,
    ]

    name = "Мониторинг"
    name_plural = "Мониторинг"
    
    form = AlertsForm
