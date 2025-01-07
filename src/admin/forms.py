from wtforms import Form, PasswordField, SelectField, StringField
from wtforms.validators import InputRequired

from src.db.models import UrlEnum
from src.dependencies import get_password_hasher


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


class APIUrlsCreateForm(Form):
    main_url = StringField("ID приложения", validators=[InputRequired()])
    main_url_status = SelectField(
        "ID приложения", choices=[(e.value, e.value) for e in UrlEnum], validators=[InputRequired()]
    )
    reverse_url = StringField("ID приложения", validators=[InputRequired()])
    reverse_url_status = SelectField(
        "ID приложения", choices=[(e.value, e.value) for e in UrlEnum], validators=[InputRequired()]
    )

    def populate_obj(self, obj):
        super().populate_obj(obj)
        print(obj.__dict__)
        # obj.main_url_status = UrlEnum.__getattribute__(obj.main_url_status)
