from fastapi import FastAPI,Depends,HTTPException
import services,models,schemas
from db import get_db,engine,create_table
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/Tasks/",response_model=list[schemas.Task])
async def get_all_tasks(db:Session=Depends(get_db)):
    return services.get_tasks(db)
@app.post("/Tasks/",response_model=schemas.Task)
async def create_new_tasks(task:schemas.Taskcreate,db:Session=Depends(get_db)):
    create_table()
    return services.create_tasks(db,task)
@app.get("/Tasks/{id}",response_model=schemas.Task)
async def get_one_tasks(id : int,db:Session=Depends(get_db)):
    a=services.get_one(db,id)
    if a:
        return a
    raise HTTPException(status_code=404,detail="invalid task id given")
@app.put("/Tasks/{id}",response_model=schemas.Task)
async def update_task(task:schemas.Taskcreate,id:int,db:Session=Depends(get_db)):
    b=services.update_task_db(task,id,db)
    if b:
        return b
    raise HTTPException(status_code=404,detail="task not found")
@app.delete("/Tasks/{id}",response_model=schemas.Task)
async def delete_task(id:int,db:Session=Depends(get_db)):
    c=services.delete_task(id,db)
    if c:
        return c
    raise HTTPException(status_code=404,detail="Error in deleting")
