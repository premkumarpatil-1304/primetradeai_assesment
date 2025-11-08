from pydantic import BaseModel, Field
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: str

class TaskCreate(TaskBase):
    pass

class TaskInDB(TaskBase):
    owner: str
    id: Optional[str] = Field(alias="_id")

class TaskOut(TaskBase):
    id: str
    owner: str
