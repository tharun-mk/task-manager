from pydantic import BaseModel, EmailStr
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

class Userbase(BaseModel):
    username: str
    email: EmailStr

class Usercreate(Userbase):
    password: str

class Userlogin(BaseModel):
    username: str
    password: str

class Userdisplay(Userbase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserWithToken(Userdisplay):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True

class OtpVerify(BaseModel):
    email: EmailStr
    otp: int