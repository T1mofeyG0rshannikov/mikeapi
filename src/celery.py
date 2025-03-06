import asyncio
import os

from celery import Celery
from src.dependencies.dependencies import get_vendor_repository
from src.entites.trader import TraderWatch
from src.db.database import get_db
from src.repositories.trader_repository import TraderRepository
from src.usecases.create_traders.create_traders import CreateTraders
from src.usecases.create_usernames import AddUsernames, CreateUsernameDTO

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


async def create_usernames(strings, watch=TraderWatch.pre, action=None) -> None:
    async for db in get_db():
        usecase = AddUsernames(TraderRepository(db), get_vendor_repository(db))

        users = []

        for i in range(0, len(strings), 2):
            users.append(CreateUsernameDTO(username=strings[i], data=strings[i + 1]))

        users = sorted(users, key=lambda u: u.username)
        await usecase(users, watch=watch, action=action)

@celery.task
def create_usernames_task(strings, watch=TraderWatch.pre, action=None):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_usernames(strings, watch, action))

    

async def create_traders(strings) -> None:
    async for db in get_db():
        usecase = CreateTraders(TraderRepository(db))
        await usecase(strings)

@celery.task
def create_traders_task(strings):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_traders(strings))