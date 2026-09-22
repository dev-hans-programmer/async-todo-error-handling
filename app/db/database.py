from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config_settings.settings import settings

# <driver>://username:password@<host>:port/<db_name>

# environment multipel
# How to manage different environments: dev, qa, prod

engine = create_async_engine(url=settings.DATABASE_URL)

Session = async_sessionmaker(bind=engine, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with Session() as session:
        yield session  # this is generator pausible object


async def create_tables():

    from app.models.todo import Todo
    from app.models.user import User

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
