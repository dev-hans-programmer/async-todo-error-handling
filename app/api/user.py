
from fastapi import APIRouter, HTTPException, status

from app.dependencies.user_dependency import UserServiceDependency
from app.schema.user_schema import Credentials, UserCreate, UserResponse
from app.security import create_access_token
from app.dependencies.security_dependency import CurrentUser

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
    # jwt token
    # header + payload + signature
    # This token is created based on some secret

    token = create_access_token(user.id)

    return {"token": token}


# before you even reach the endpoint, if you have to do some processing or anything
# we will have to use sth called a middleware
# middleware is a function or codeblock which runs after receving the request and before returning response

# assignment 1: Create a middleware which will calculate the total time taken for any request


@router.get('/me')
async def get_me(current_user: CurrentUser):
    return {"user":current_user} 

