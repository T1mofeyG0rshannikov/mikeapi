from typing import List
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
    diapazon_filter_fields = []
    page_size = 100

    @action(name="delete_all", label="Удалить (фильтр)", confirmation_message="Вы уверены?")
    async def delete_all_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            await session.execute(delete(self.model).where(self.filters_from_request(request)))
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)

    def filters_from_request(self, request: Request):
        filters = and_()

        for f in self.diapazon_filter_fields:
            diapazon_field_name = str(f).split(".")[1]
            print(diapazon_field_name)
            diapazon_field_request_l = request.query_params.get(f"{diapazon_field_name}_l", None)
            diapazon_field_request_r = request.query_params.get(f"{diapazon_field_name}_r", None)

            if diapazon_field_request_l:
                filters &= and_(float(diapazon_field_request_l) <= getattr(self.model, diapazon_field_name))
            if diapazon_field_request_r:
                filters &= and_(getattr(self.model, diapazon_field_name) <= float(diapazon_field_request_r))

        return filters
    
    def get_diapazon_columns(self) -> List[str]:
        """Get list of properties to display in List page."""
        column_list = getattr(self, "diapazon_filter_fields", None)

        return self._build_column_list(
            include=column_list,
            exclude=[],
            defaults=[pk.name for pk in self.pk_columns],
        )
    
    def __init__(self) -> None:
        super().__init__()
        self._filter_diapazon_list = self.get_diapazon_columns()

    async def list(self, request: Request) -> Pagination:
        page = self.validate_page_number(request.query_params.get("page"), 1)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), 0)
        page_size = min(page_size or self.page_size, max(self.page_size_options))

        stmt = self.list_query(request).filter(self.filters_from_request(request))
        for relation in self._list_relations:
            stmt = stmt.options(selectinload(relation))
            stmt = stmt.join(relation)

        count = await self.count(request, select(func.count()).select_from(stmt))
        stmt = self.sort_query(stmt, request)

        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        rows = await self._run_query(stmt)

        pagination = Pagination(
            rows=rows,
            page=page,
            page_size=page_size,
            count=count,
        )

        return pagination


def format_sum(num: float) -> str:
    if abs(num) // 1_000_000 > 0:
        num = round(num / 1_000_000, 1)
        if num == int(num):
            num = int(num)
        return f"{num}M"
    if abs(num) // 1_000 > 0:
        num = round(num / 1_000, 1)
        if num == int(num):
            num = int(num)
        return f"{num}K"

    num = round(num, 2)
    if num == int(num):
        num = int(num)
    return str(num)


DEGREES_COLORS = {
    "more": "(20, 215, 20)",
    "less": "(255, 100, 100)"
}

def render_profit(value: int | None) -> str:
    if value is None:
        return ""
    
    if value == 0:
        return ""
    
    value_format = format_sum(value)
    
    return f'''<span style="color: rgb{DEGREES_COLORS["more" if value > 0 else "less"]}">{value_format}</span>'''


def render_degrees(value: int | None) -> str:
    if value is None:
        return ""
    
    if value == 0:
        return ""

    value_format = format_sum(value)

    return f'''<span style="color: rgb{DEGREES_COLORS["more" if value > 0 else "less"]}">({value_format if value < 0 else f"+{value_format}"})</span>'''
