from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.repo.todo_repo import TodoRepo
from app.service.todo_service import TodoService


def get_todo_service(db: Annotated[AsyncSession, Depends(get_db)]):
    return TodoService(TodoRepo(db=db))

TodoServiceDependency = Annotated[TodoService, Depends(get_todo_service)]