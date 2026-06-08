from db import Base
import enum
from sqlalchemy import Integer, Column, String, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship

class TaskStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Tasks(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_to_do = Column(String, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    due_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="tasks")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False, unique=True)
    password = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False, unique=True)
    tasks = relationship("Tasks", back_populates="owner")
