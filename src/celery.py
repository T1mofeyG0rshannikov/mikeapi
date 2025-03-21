import asyncio
import os

from celery import Celery
from src.dependencies.container import Container
from src.entites.trader import TraderWatch
from src.usecases.create_usernames import CreateUsernameDTO

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


async def create_usernames(strings, watch=TraderWatch.pre, action=None) -> None:
    usecase = await Container.add_usernames()
    users = [CreateUsernameDTO(username=strings[i], data=strings[i + 1]) for i in range(0, len(strings), 2)]
    users = sorted(users, key=lambda u: u.username)
    await usecase(users, watch=watch, action=action)


@celery.task
def create_usernames_task(strings, watch=TraderWatch.pre, action=None):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_usernames(strings, watch, action))


async def create_traders(strings) -> None:
    usecase = await Container.create_traders()
    await usecase(strings)


@celery.task
def create_traders_task(strings):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_traders(strings))