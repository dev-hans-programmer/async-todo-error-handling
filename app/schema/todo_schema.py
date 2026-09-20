from pydantic import BaseModel


class TodoCreate(BaseModel):
    name: str
    description: str | None = None
    is_completed: bool

class TodoUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_completed: bool | None = None



# Write db models
# Write pydantic schema
# Write repo layer
# Write service layer
# write apu layer
# write config loader