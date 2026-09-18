from fastapi import APIRouter, Depends
from app.db.database import get_db

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from sqlalchemy import select
from app.models.todo import Todo

router = APIRouter(prefix='/todos')

from pydantic import BaseModel



# 1. Whenever we have external resources to use in any routes or functions
# we use that as a dependency which basically implies that we are using dependency injection

# we have to use that db instance
# from there we can call the sqlalchemy methods based on our need

# localhost:9000/todos

# We can annotated to use the desired type


MyDbSession = Annotated[AsyncSession, Depends(get_db)]


class TodoCreate(BaseModel):
    name: str
    description: str | None = None
    is_completed: bool


@router.get('/')
async def get_todos(session: MyDbSession):
    # fetch all the todos:

    print(f"SESSION {session}")
    result = await session.execute(select(Todo))
    return list(result.scalars().all())

@router.post('/')
async def create_todo(todo_in: TodoCreate, session: MyDbSession):
    print(f"TOOD CREATE {todo_in}")

    # create a todo instance and provide to this function
    created_todo = Todo(**todo_in.model_dump())

    print(f"CREATED TODO {created_todo}")
    session.add(created_todo)

    await session.commit()

    # we can refresh the newly created data
    await session.refresh(created_todo)


    return {"message":"Todo has been created"}

# CREATE, GET, PATCH, DELETE
