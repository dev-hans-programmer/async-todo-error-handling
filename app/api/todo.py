from fastapi import APIRouter, Query
from typing import Annotated

from app.dependencies.security_dependency import CurrentUser
from app.dependencies.todo_dependency import TodoServiceDependency
from app.schema.common_schema import SuccessResponse
from app.schema.todo_schema import TodoCreate, TodoResponse, TodoUpdate, TodoListParams
from app.utils.responses import success_response

router = APIRouter(prefix="/todos")

# 1. We have broken down our codebase into layers
# 2. Every layer is independently testable


# 1. Whenever we have external resources to use in any routes or functions
# we use that as a dependency which basically implies that we are using dependency injection

# we have to use that db instance
# from there we can call the sqlalchemy methods based on our need

# localhost:9000/todos

# We can annotated to use the desired type

"""
Currently this file is handling too many things:
1. HTTP requests
2. It's doing any kind of business logic
3. It's interacting with the db(persistence logic)

In order to solve this, we can introduce sth called repository pattern.
In this pattern, we break down the entire application into majorly 3 layers
1. API - Handling api requests
2. Service -> We handle all the business logic
3. Repository -> Here, we only care about of persisting or retriving data from any source(db, filesystem source, external api as a source)

"""


@router.get("/", response_model=SuccessResponse[list[TodoResponse]])
async def get_todos(
    service: TodoServiceDependency,
    current_user: CurrentUser,
    filters: Annotated[TodoListParams, Query()],
):
    # fetch all the todos:
    user_id = current_user.id

    todos, total = await service.fetch_all_todos(user_id, filters)
    total_pages = (total + filters.limit - 1) // filters.limit
    return success_response(data=todos, message="Todos fetched successfully", meta={
        "page": filters.page,
        "limit": filters.limit,
        "total_items": total,
        "total_pages": total_pages,
        "has_next": filters.page < total_pages,
        "has_previous": filters.page > 1
    })


@router.post("/")
async def create_todo(
    todo_in: TodoCreate, service: TodoServiceDependency, current_user: CurrentUser
):
    user_id = current_user.id
    created_todo = await service.create_todo(todo_in, user_id)
    return {"message": f"Todo has been created with id {created_todo.id}"}


@router.patch("/{todo_id}")
async def update_todo(
    todo_id: int, todo_in: TodoUpdate, service: TodoServiceDependency
):
    return await service.update_todo(todo_id, todo_in)


# Fetch all todos
# Delete all todos

# CREATE, GET, PATCH, DELETE
