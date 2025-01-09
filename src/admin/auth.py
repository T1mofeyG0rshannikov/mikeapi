from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from src.admin.config import get_admin_config
from src.dependencies import get_jwt_processor, get_password_hasher
from src.depends.func_depends import get_user_repository
from src.repositories.user_repository import UserRepository
from src.schemas.login import LoginResponse


class AdminAuth(AuthenticationBackend):
    password_hasher = get_password_hasher()
    jwt_processor = get_jwt_processor()
    config = get_admin_config()

    async def login(self, request: Request, user_repository: UserRepository = get_user_repository()) -> LoginResponse:
        if self.config.debug:
            return True

        form = await request.form()
        email, password = form["email"], form["password"]

        user = await user_repository.get(email=email)
        if not user:
            return LoginResponse(ok=False, email_error_message=f"нет пользователя с email адресом {email}")

        if not user.is_superuser:
            return LoginResponse(ok=False, email_error_message="Недостаточно прав для входа в панель администратора")

        if not self.password_hasher.verify(password, user.hash_password):
            return LoginResponse(ok=False, password_error_message="Неверный пароль")

        access_token = self.jwt_processor.create_access_token(user.email, user.id)
        print(access_token)
        request.session.update({"token": access_token})
        return LoginResponse(ok=True)

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        if self.config.debug:
            return True

        token = request.session.get("token")

        if token and self.jwt_processor.validate_token(token):
            return True

        return False
