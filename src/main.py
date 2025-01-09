from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.admin.config import get_admin_config
from src.exc_handler import init_exc_handlers
from src.init_admin import init_admin
from src.routes.log_route import router as log_router
from src.routes.traders_route import router as traders_router

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=get_admin_config().admin_secret_key)

app.include_router(router=log_router)
app.include_router(router=traders_router)

init_admin(app)
init_exc_handlers(app)
