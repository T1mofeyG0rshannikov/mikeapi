from contextlib import asynccontextmanager
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.admin.config import get_admin_config
from src.create_log_activity import create_log_activity
from src.exc_handler import init_exc_handlers
from src.init_admin import init_admin
from src.routes.log_route import router as log_router
from src.routes.traders_route import router as traders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        timezone = pytz.timezone("Europe/Moscow")
        # scheduler = AsyncIOScheduler(timezone=timezone)
        scheduler = BackgroundScheduler(timezone=timezone)

        scheduler.add_job(create_log_activity, "cron", hour="*", minute="*")

        scheduler.start()
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=get_admin_config().admin_secret_key)

app.include_router(router=log_router)
app.include_router(router=traders_router)

init_admin(app)
init_exc_handlers(app)
