from fastapi import Request, Response
from sqladmin import Admin
from sqladmin.authentication import login_required
from starlette.responses import RedirectResponse


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
    async def list(self, request: Request) -> Response:
        """List route to display paginated Model instances."""

        await self._list(request)

        model_view = self._find_model_view(request.path_params["identity"])
        pagination = await model_view.list(request)
        pagination.add_pagination_urls(request.url)

        request_page = model_view.validate_page_number(request.query_params.get("page"), 1)

        if request_page > pagination.page:
            return RedirectResponse(request.url.include_query_params(page=pagination.page), status_code=302)

        context = {"model_view": model_view, "pagination": pagination, "ticker_types": ""}
        return await self.templates.TemplateResponse(request, model_view.list_template, context)
