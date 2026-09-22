
from fastapi import APIRouter, HTTPException, status

from app.dependencies.user_dependency import UserServiceDependency
from app.schema.user_schema import Credentials, UserCreate, UserResponse

router = APIRouter(prefix='/users')

# primary:
# 1. normal integer(auto incremented)
# uuid: UUID is unique by default

# assigment: 




# register
@router.post('/register', response_model=UserResponse) # /users/register
async def register(user_in: UserCreate, service: UserServiceDependency):
    return await service.register(user_in)

@router.post('/login')
async def login(credentials:Credentials, service: UserServiceDependency ):
    user = await service.authenticate(credentials.email, credentials.password)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # TODO: you want to create and return some kind of token
    # TODO: what is token, what is jwt, what are other types of authentication, which one to use and why
    # TODO: Build some great auth system

    return {"message":"You are logged in", "user": user}


    

