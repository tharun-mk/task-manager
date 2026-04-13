from db import Base
import enum
from sqlalchemy import Integer,Column,String,Enum,Date
class TaskStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
class Tasks(Base):
    __tablename__="tasks"
    id=Column(Integer,primary_key=True,index=True)
    task_to_do=Column(String,index=True)
    status=Column(Enum(TaskStatus),default=TaskStatus.PENDING,nullable=False)
    due_date = Column(Date, nullable=True)