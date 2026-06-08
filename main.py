from fastapi import FastAPI, Depends, HTTPException
import services, models, schemas
from db import get_db, engine, create_table
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    yield
app=FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tharun-mk.github.io","https://tharun-mk.github.io/task-manager","http://127.0.0.1:8000","http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/Tasks/", response_model=list[schemas.Task])
async def get_all_tasks(username: str, db: Session = Depends(get_db)):
    return services.get_tasks(db, username)

@app.post("/Tasks/", response_model=schemas.Task)
async def create_new_tasks(task: schemas.Taskcreate, username: str, db: Session = Depends(get_db)):
    create_table()
    return services.create_tasks(db, task, username)

@app.get("/Tasks/{id}", response_model=schemas.Task)
async def get_one_tasks(id: int, username: str, db: Session = Depends(get_db)):
    a = services.get_one(db, id, username)
    if a:
        return a
    raise HTTPException(status_code=404, detail="invalid task id given")

@app.put("/Tasks/{id}", response_model=schemas.Task)
async def update_task(task: schemas.Taskcreate, id: int, username: str, db: Session = Depends(get_db)):
    b = services.update_task_db(task, id, db, username)
    if b:
        return b
    raise HTTPException(status_code=404, detail="task not found")

@app.delete("/Tasks/{id}", response_model=schemas.Task)
async def delete_task(id: int, username: str, db: Session = Depends(get_db)):
    c = services.delete_task(id, db, username)
    if c:
        return c
    raise HTTPException(status_code=404, detail="Error in deleting")

@app.post("/signup/")
async def signup(user: schemas.Usercreate, db: Session = Depends(get_db)):
    return services.start_signup_otp(db, user.username, user.email, user.password)

@app.post("/login/", response_model=schemas.Userdisplay)
async def login(credentials: schemas.Userlogin, db: Session = Depends(get_db)):
    user = services.login_user(db, credentials.username, credentials.password)
    if user:
        return user
    raise HTTPException(status_code=404, detail="Invalid username or password")

@app.post("/verify-otp/", response_model=schemas.Userdisplay)
async def verify_otp(data: schemas.OtpVerify, db: Session = Depends(get_db)):
    user = services.verify_otp(db, data.email, data.otp)
    return user
