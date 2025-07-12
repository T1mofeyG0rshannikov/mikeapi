from fastapi import Request, Response
from sqladmin import Admin
from sqladmin.authentication import login_required
from sqlalchemy import select, func
from starlette.responses import RedirectResponse

from src.db.models.models import ServerUnavailableLogOrm, UnsuccessLog
from src.db.database import Session
from src.dependencies.container import Container


class CustomAdmin(Admin):
    async def login(self, request: Request) -> Response:
        assert self.authentication_backend is not None

        context = {}
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "sqladmin/login.html")

        response = await self.authentication_backend.login(request)
        if not response.ok:
            context["email_error_message"] = response.email_error_message
            context["password_error_message"] = response.password_error_message
            return await self.templates.TemplateResponse(request, "sqladmin/login.html", context, status_code=400)

        return RedirectResponse(request.url_for("admin:index"), status_code=302)
    
    @login_required
    async def index(self, request: Request) -> Response:
        """Index route which can be overridden to create dashboards."""
        db = Session()
        redis = Container.redis()
        last_seen_count = redis.get('last_seen_failure_trades')
        if last_seen_count is None:
            last_seen_count = 0
        else:
            last_seen_count = int(last_seen_count)

        logs_count = db.execute(select(func.count(UnsuccessLog.id))).scalar_one()
        new_obj_count = logs_count - last_seen_count
        request.session['new_failure_trades'] = new_obj_count


        errors_count = db.execute(select(func.count(ServerUnavailableLogOrm.id))).scalar_one()
        last_seen_count = redis.get('last_seen_errors')
        if last_seen_count is None:
            last_seen_count = 0
        else:
            last_seen_count = int(last_seen_count)

        new_obj_count = errors_count - last_seen_count
        request.session['new_errors'] = new_obj_count

        return await self.templates.TemplateResponse(request, "sqladmin/index.html")

    @login_required
    async def list(self, request: Request) -> Response:
        """List route to display paginated Model instances."""
        await self._list(request)

        db = Session()
        redis = Container.redis()
        last_seen_count = redis.get('last_seen_failure_trades')
        if last_seen_count is None:
            last_seen_count = 0
        else:
            last_seen_count = int(last_seen_count)

        logs_count = db.execute(select(func.count(UnsuccessLog.id))).scalar_one()
        new_obj_count = logs_count - last_seen_count
        request.session['new_failure_trades'] = new_obj_count


        errors_count = db.execute(select(func.count(ServerUnavailableLogOrm.id))).scalar_one()
        last_seen_count = redis.get('last_seen_errors')
        if last_seen_count is None:
            last_seen_count = 0
        else:
            last_seen_count = int(last_seen_count)

        new_obj_count = errors_count - last_seen_count
        request.session['new_errors'] = new_obj_count


        model_view = self._find_model_view(request.path_params["identity"])
        pagination = await model_view.list(request)
        pagination.add_pagination_urls(request.url)

        request_page = model_view.validate_page_number(request.query_params.get("page"), 1)

        if request_page > pagination.page:
            return RedirectResponse(request.url.include_query_params(page=pagination.page), status_code=302)

        context = {"model_view": model_view, "pagination": pagination}
        return await self.templates.TemplateResponse(request, model_view.list_template, context)
