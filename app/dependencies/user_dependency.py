from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.repo.user_repo import UserRepository
from app.service.user_service import UserService


def get_user_service(db:Annotated[AsyncSession,Depends(get_db) ]):
    return UserService(UserRepository(db))

UserServiceDependency = Annotated[UserService, Depends(get_user_service)]

