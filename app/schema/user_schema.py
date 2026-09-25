from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    email :str

class MeResponse(BaseModel):
    id: int
    email: str

class Credentials(BaseModel):
    email: EmailStr
    password: str