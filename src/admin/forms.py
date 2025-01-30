from wtforms import (
    DateField,
    Form,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
)
from wtforms.validators import InputRequired
from wtforms.validators import Optional
from src.dependencies import get_password_hasher
from src.entites.ticker import TICKER_TYPES


class UserCreateForm(Form):
    username = StringField("Username", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

    password_hasher = get_password_hasher()

    def validate_password(form, field):
        if not field.data:
            raise ValueError("Password is Required")

        if len(field.data) < 8:
            raise ValueError("Password length should be more than 7 symbol")

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
