from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    name: str
    description: str | None = None
    is_completed: bool

class TodoUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_completed: bool | None = None

class TodoResponse(BaseModel):
    id: int
    name: str
    description: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime

class TodoListParams(BaseModel):
    is_completed: bool | None = None
    sort_by: Literal["created_at","name"] = "created_at"
    sort_order:Literal["asc","desc"] = "asc"

    limit: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)

# Write db models
# Write pydantic schema
# Write repo layer
# Write service layer
# write apu layer
# write config loader