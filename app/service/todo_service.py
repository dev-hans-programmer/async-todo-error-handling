from app.models.todo import Todo
from app.repo.todo_repo import TodoRepo
from app.schema.todo_schema import TodoCreate, TodoListParams, TodoUpdate


class TodoService:
    def __init__(self, repo: TodoRepo):
        self.todo_repo = repo

    async def fetch_all_todos(self, user_id: int, filters: TodoListParams):
        return await self.todo_repo.get_all(user_id, filters)

    async def create_todo(self, todo_in: TodoCreate, user_id: int):
        actual_todo_obj = Todo(**todo_in.model_dump(), user_id=user_id)
        created_todo = await self.todo_repo.create(actual_todo_obj)
        return created_todo

    async def update_todo(self, todo_id: int, todo_in:TodoUpdate ):
        # find the todo
        desired_todo = await self.todo_repo.get_by_id(todo_id)


        changes = todo_in.model_dump(exclude_unset=True)

        return await self.todo_repo.update(desired_todo, changes)

        