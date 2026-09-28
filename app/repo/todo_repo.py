from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo
from app.schema.todo_schema import TodoListParams


class TodoRepo:
    # dependency injection
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id: int, filters: TodoListParams) -> list[Todo]:
        stmt = select(Todo).where(Todo.user_id == user_id)

        if filters.is_completed is not None:
            stmt = stmt.where(Todo.is_completed == filters.is_completed)

        sort_columns = {"created_at": Todo.created_at, "name": Todo.name}

        sort_column = sort_columns[filters.sort_by]

        ordering = (
            sort_column.asc() if filters.sort_order == "asc" else sort_column.desc()
        )

        offset = (filters.page - 1) * filters.limit
        limit = filters.limit

        stmt = stmt.order_by(ordering).offset(offset).limit(limit)

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def create(self, todo: Todo):
        self.db.add(todo)

        await self.db.commit()
        await self.db.refresh(todo)
        return todo

    async def update(self, todo: Todo, changes: dict[str, Any]):
        for field, value in changes.items():
            setattr(todo, field, value)

        await self.db.commit()

        await self.db.refresh(todo)

        return todo

    async def get_by_id(self, todo_id: int):
        query = select(Todo).where(Todo.id == todo_id)
        # SELECT todo from todos_table where todos_table.id = todo_id

        return (await self.db.execute(query)).scalar_one_or_none()
