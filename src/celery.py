import asyncio
import os

from celery import Celery
from src.create_usernames import AddUsernames, CreateUsernameDTO
from src.db.database import SessionLocal
from src.repositories.trader_repository import TraderRepository

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task
def create_usernames_task(strings):
    db = SessionLocal()
    usecase = AddUsernames(TraderRepository(db))

    users = []

    for i in range(0, len(strings), 2):
        users.append(CreateUsernameDTO(username=strings[i], data=strings[i + 1]))

    users = sorted(users, key=lambda u: u.username)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(usecase(users))