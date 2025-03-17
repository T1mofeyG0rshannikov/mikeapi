from sqladmin import ModelView

from src.db.models.models import ServerUnavailableLogOrm
from starlette.requests import Request
from sqladmin.pagination import Pagination
from src.dependencies.container import Container


class ServerLogAdmin(ModelView, model=ServerUnavailableLogOrm):
    column_list = [ServerUnavailableLogOrm.id, ServerUnavailableLogOrm.log]

    name = "Системные сбои"
    name_plural = "Системные сбои"

    column_default_sort = ("id", "desc")

    page_size = 100
    marker = True
    marker_key = 'new_errors'
    
    async def list(self, request: Request) -> Pagination:
        pagination = await super().list(request)
        redis = Container.redis()
        last_seen_count = redis.get('last_seen_errors')
        if last_seen_count is None:
            last_seen_count = 0
        else:
            last_seen_count = int(last_seen_count)

        new_obj_count = pagination.count - last_seen_count
        redis.set('last_seen_errors', pagination.count)
        request.session['new_errors'] = new_obj_count
        
        return pagination
