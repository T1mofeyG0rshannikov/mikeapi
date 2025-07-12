import asyncio
from getpass import getpass
from typing import Annotated

from dependencies.decorator import inject_dependencies
from src.repositories.user_repository import UserRepository
from src.dependencies.repos_container import ReposContainer
from src.dependencies.base_dependencies import get_password_hasher
from mikeapi.src.user.password_hasher import PasswordHasher


@inject_dependencies
async def create_admin_user(
    username,
    email,
    password,
    user_repository: Annotated[UserRepository, ReposContainer.user_repository],
    password_hasher: PasswordHasher = get_password_hasher(),
) -> None:
    hashed_password = password_hasher.hash_password(password)
    await user_repository.create(username=username, email=email, hashed_password=hashed_password, is_superuser=True)
    print(f"User '{username}' successfully created!")


if __name__ == "__main__":
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = getpass("Enter password: ")

    asyncio.run(create_admin_user(username, email, password))
