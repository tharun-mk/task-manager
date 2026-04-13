from models import Tasks
from sqlalchemy.orm import Session
from schemas import Taskcreate
def create_tasks(db:Session,data:Taskcreate):
    task_instance=Tasks(**data.model_dump())
    db.add(task_instance)
    db.commit()
    db.refresh(task_instance)
    return task_instance
def get_tasks(db:Session):
    return db.query(Tasks).all()
def get_one(db:Session,taskid:int):
    return db.query(Tasks).filter(Tasks.id==taskid).first()
def update_task_db(data,id,db):
    t=db.query(Tasks).filter(Tasks.id==id).first()
    if t:
        for key,value in data.model_dump().items():
            setattr(t,key,value)
        db.commit()
        db.refresh(t)
    return t
def delete_task(id,db):
    q=db.query(Tasks).filter(Tasks.id==id).first()
    if q:
        db.delete(q)
        db.commit()
    return q
