from src.admin.forms import ContactForm
from src.admin.model_views.base import BaseModelView
from src.db.models.models import ContactOrm


class ContactAdmin(BaseModelView, model=ContactOrm):
    column_list = [ContactOrm.channel, ContactOrm.contact]

    name = "Контакты"
    name_plural = "Контакты"
    
    form = ContactForm
