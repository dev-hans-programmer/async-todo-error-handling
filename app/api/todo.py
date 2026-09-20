
from fastapi import APIRouter

from app.dependencies.todo_dependency import TodoServiceDependency
from app.schema.todo_schema import TodoCreate, TodoUpdate

router = APIRouter(prefix='/todos')

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

@router.get('/')
async def get_todos(service:TodoServiceDependency ):
    # fetch all the todos:

    todos = await service.fetch_all_todos()
    return {"todos": todos}

@router.post('/')
async def create_todo(todo_in: TodoCreate, service: TodoServiceDependency):
    created_todo = await service.create_todo(todo_in)
    return {"message":f"Todo has been created with id {created_todo.id}"}


@router.patch('/{todo_id}')
async def update_todo(todo_id: int, todo_in: TodoUpdate,service: TodoServiceDependency):
    return await service.update_todo(todo_id, todo_in)

# Fetch all todos
# Delete all todos

# CREATE, GET, PATCH, DELETE
