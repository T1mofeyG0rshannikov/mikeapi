from wtforms import (
    DateField,
    Form,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField
)
from wtforms.validators import InputRequired, Optional

from src.dependencies.base_dependencies import get_password_hasher
from src.entites.schedler import WeekDays
from src.entites.alert import AlertChannels
from src.entites.contacts import ContactChannel
from src.entites.ticker import TICKER_TYPES


class UserCreateForm(Form):
    username = StringField("Username", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

    password_hasher = get_password_hasher()

    def validate_password(form, field):
        if not field.data:
            raise ValueError("Password is Required")

        if len(field.data) < 6:
            raise ValueError("Password length should be more than 5 symbol")

    def populate_obj(self, obj):
        super().populate_obj(obj)
        obj.hash_password = self.password_hasher.hash_password(obj.password)


class VendorCreateForm(Form):
    app_id = StringField("ID приложения", validators=[InputRequired()])
    auth_token = StringField("Токен авторизации", validators=[InputRequired()])


class TickerForm(Form):
    slug = StringField("Тикер", validators=[InputRequired()])
    name = StringField("Название")

    types = [(type_["value"], type_["name"]) for type_ in TICKER_TYPES]

    lot = IntegerField("Лот")
    type = SelectField("Тип", choices=types)
    currency = StringField("Валюта")
    end = DateField("Конец", validators=[Optional()])


class ContactForm(Form):
    channel = SelectField("Тип", choices=ContactChannel.values_list)
    contact = StringField("Контакт")
    recipient = StringField("Получатель")


class AlertsForm(Form):
    first_log = StringField("Нет сделок 1: <текст>", render_kw={"style": "width: 500px;"})
    first_log_channel = SelectField("Нет сделок 1: <тип>", choices=AlertChannels.values_list)
    
    second_log = StringField("Нет сделок 2: <текст>", render_kw={"style": "width: 500px;"})
    second_log_channel = SelectField("Нет сделок 2: <тип>", choices=AlertChannels.values_list)
    
    first_ping = StringField("Нет пинга 1: <текст>", render_kw={"style": "width: 500px;"})
    first_ping_channel = SelectField("Нет пинга 1: <тип>", choices=AlertChannels.values_list)
    
    second_ping = StringField("Нет пинга 2: <текст>", render_kw={"style": "width: 500px;"})
    second_ping_channel = SelectField("Нет пинга 2: <тип>", choices=AlertChannels.values_list)
    
    trades_recovered = StringField("Сделки восстановлены: <текст>", render_kw={"style": "width: 500px;"})
    trades_recovered_channel = SelectField("Сделки восстановлены: <тип>", choices=AlertChannels.values_list)
    
    pings_recovered = StringField("Пинги восстановлены: <текст>", render_kw={"style": "width: 500px;"})
    pings_recovered_channel = SelectField("Пинги восстановлены: <тип>", choices=AlertChannels.values_list)
    
    pings_interval1 = IntegerField("Пинги интервал 1")
    pings_interval2 = IntegerField("Пинги интервал 2")


class SchedulerForm(Form):
    day_l = SelectField("день от", choices=WeekDays.values_list)
    day_r = SelectField("день от", choices=WeekDays.values_list)
    
    hour_l = IntegerField()
    minute_l = IntegerField()

    hour_r = IntegerField()
    minute_r = IntegerField()
    
    interval1 = IntegerField()
    interval2 = IntegerField()