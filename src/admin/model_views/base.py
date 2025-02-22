from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action
from sqladmin.helpers import slugify_class_name
from sqladmin.pagination import Pagination
from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload

from sqlalchemy import (
    and_,
    delete,
    func
)


class BaseModelView(ModelView):
    @action(name="delete_all", label="Удалить (фильтр)", confirmation_message="Вы уверены?")
    async def delete_all_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            await session.execute(delete(self.model).where(self.filters_from_request(request)))
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)

    def filters_from_request(self, request: Request):
        return and_()

    async def list(self, request: Request) -> Pagination:
        page = self.validate_page_number(request.query_params.get("page"), 1)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), 0)
        page_size = min(page_size or self.page_size, max(self.page_size_options))

        stmt = self.list_query(request).filter(self.filters_from_request(request))
        for relation in self._list_relations:
            stmt = stmt.options(selectinload(relation))

        stmt = self.sort_query(stmt, request)

        count = await self.count(request, select(func.count()).select_from(stmt))

        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        rows = await self._run_query(stmt)

        pagination = Pagination(
            rows=rows,
            page=page,
            page_size=page_size,
            count=count,
        )

        return pagination