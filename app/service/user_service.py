from fastapi import HTTPException, status

from app.models.user import User
from app.repo.user_repo import UserRepository
from app.schema.user_schema import UserCreate
from app.security import hash_password, verify_password

from app.errors.exceptions import UserAlreadyExists
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register(self, user_in: UserCreate):
        # firstly we will have to check whether we are already registered
        # if not then create the user and return it
        existing = await self.repo.get_by_email(user_in.email)

        if existing is not None:
            raise UserAlreadyExists()


        # create it
        user_dict = user_in.model_dump()

        user_model_obj = User(email =user_dict['email'], password_hash=hash_password(user_dict['password']))

        print(user_model_obj.email)

        return await self.repo.create(user_model_obj)

    async def authenticate(self, email: str, password: str):
        existing_user = await self.repo.get_by_email(email)

        if not existing_user:
            return None

        # if Yes, then verify the password
        is_verified = verify_password(password, existing_user.password_hash)

        if is_verified:
            return existing_user

        return None

    async def has_changed_password():
        pass

