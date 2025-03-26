from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.dependencies.base_dependencies import get_admin_config
from src.admin.init import init_admin
from src.background_tasks.init import init_scheduler
from src.exc_handler import init_exc_handlers
from src.routes.log_route import router as log_router
from src.routes.traders_route import router as traders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_scheduler()
    init_admin(app)
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.add_middleware(SessionMiddleware, secret_key=get_admin_config().admin_secret_key)

app.include_router(router=log_router)
app.include_router(router=traders_router)
init_exc_handlers(app)