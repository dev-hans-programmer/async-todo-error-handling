from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo


class TodoRepo:
    # dependency injection
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Todo]:
        result = await self.db.execute(select(Todo))
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


    