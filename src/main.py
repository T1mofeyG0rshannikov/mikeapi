from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db.database import create_tables, delete_tables
from src.exc_handler import init_exc_handlers
from src.init_admin import init_admin
from src.routes.log_route import router as log_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=log_router)

init_admin(app)
init_exc_handlers(app)
