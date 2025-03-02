import asyncio
from getpass import getpass

from src.dependencies.base_dependencies import get_password_hasher, get_user_repository
from src.password_hasher import PasswordHasher
from src.repositories.user_repository import UserRepository


async def create_admin_user(
    username,
    email,
    password,
    user_repository: UserRepository = get_user_repository(),
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
