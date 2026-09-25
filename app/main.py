from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.todo import router as todo_router
from app.api.user import router as user_router
from app.config_settings.settings import settings
from app.db.database import create_tables, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(settings)
    # await create_tables()

    yield
    # close db engine, or any resource cleanup
    await engine.dispose()

     



app = FastAPI(lifespan=lifespan)


@app.get('/')
async def root():
    return {"message":"This is a route endpoint"}

app.include_router(todo_router)
app.include_router(user_router)