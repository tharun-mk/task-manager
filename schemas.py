from pydantic import BaseModel
from datetime import date
from typing import Optional
from models import TaskStatus
class Taskbase(BaseModel):
    id: Optional[int] = None
    task_to_do: str
    status: TaskStatus
    due_date: Optional[date] = None
class Taskcreate(Taskbase):
    pass
class Task(Taskbase):
    class Config:
        from_attributes = True
