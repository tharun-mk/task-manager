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
async def get_all_tasks(current_user: models.User = Depends(services.get_current_user), db: Session = Depends(get_db)):
    return services.get_tasks(db, current_user.id)

@app.post("/Tasks/", response_model=schemas.Task)
async def create_new_tasks(task: schemas.Taskcreate, current_user: models.User = Depends(services.get_current_user), db: Session = Depends(get_db)):
    create_table()
    return services.create_tasks(db, task, current_user.id)

@app.get("/Tasks/{id}", response_model=schemas.Task)
async def get_one_tasks(id: int, current_user: models.User = Depends(services.get_current_user), db: Session = Depends(get_db)):
    a = services.get_one(db, id, current_user.id)
    if a:
        return a
    raise HTTPException(status_code=404, detail="invalid task id given")

@app.put("/Tasks/{id}", response_model=schemas.Task)
async def update_task(task: schemas.Taskcreate, id: int, current_user: models.User = Depends(services.get_current_user), db: Session = Depends(get_db)):
    b = services.update_task_db(task, id, db, current_user.id)
    if b:
        return b
    raise HTTPException(status_code=404, detail="task not found")

@app.delete("/Tasks/{id}", response_model=schemas.Task)
async def delete_task(id: int, current_user: models.User = Depends(services.get_current_user), db: Session = Depends(get_db)):
    c = services.delete_task(id, db, current_user.id)
    if c:
        return c
    raise HTTPException(status_code=404, detail="Error in deleting")

@app.post("/signup/")
async def signup(user: schemas.Usercreate, db: Session = Depends(get_db)):
    return services.start_signup_otp(db, user.username, user.email, user.password)

@app.post("/login/", response_model=schemas.UserWithToken)
async def login(credentials: schemas.Userlogin, db: Session = Depends(get_db)):
    user = services.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=404, detail="Invalid username or password")
    access_token = services.create_access_token(data={"sub": user.username})
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
    }

@app.post("/verify-otp/", response_model=schemas.UserWithToken)
async def verify_otp(data: schemas.OtpVerify, db: Session = Depends(get_db)):
    user = services.verify_otp(db, data.email, data.otp)
    access_token = services.create_access_token(data={"sub": user.username})
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
    }
