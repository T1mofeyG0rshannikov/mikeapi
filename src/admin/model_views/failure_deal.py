import pytz
from markupsafe import Markup

from src.admin.model_views.base import BaseModelView
from src.dependencies.container import Container
from src.db.models.models import UnsuccessLog

from starlette.requests import Request
from sqladmin.pagination import Pagination


class FailureDealAdmin(BaseModelView, model=UnsuccessLog):
    column_list = [UnsuccessLog.id, UnsuccessLog.created_at, UnsuccessLog.body]

    name = "Ошибки API"
    name_plural = "Ошибки API"

    column_formatters = {
        UnsuccessLog.body: lambda m, a: Markup(f"<pre>{m.body}</pre>" if m.body else ""),
        UnsuccessLog.created_at: lambda log, _: log.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d.%m.%Y %H:%M:%S"
        ),
    }

    column_default_sort = ("id", "desc")

    page_size = 100
      
    marker = True
    marker_key = 'new_failure_trades'
    
    async def list(self, request: Request) -> Pagination:
        pagination = await super().list(request)
        redis = Container.redis()
        last_seen_count = redis.get('last_seen_failure_trades')
        if last_seen_count is None:
            last_seen_count = 0
        else:
            last_seen_count = int(last_seen_count)

        new_obj_count = pagination.count - last_seen_count
        redis.set('last_seen_failure_trades', pagination.count)
        request.session['new_failure_trades'] = new_obj_count
        
        return pagination