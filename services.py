import os
import random
import smtplib
from email.message import EmailMessage
from typing import Optional

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models import Tasks, User
from schemas import Taskcreate
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

pending_otps: dict[str, dict] = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_tasks(db: Session, data: Taskcreate, owner_username: str):
    user = db.query(User).filter(User.username == owner_username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Owner user not found")
    task_data = data.model_dump(exclude={"id"})
    task_instance = Tasks(**task_data, owner_id=user.id)
    db.add(task_instance)
    db.commit()
    db.refresh(task_instance)
    return task_instance


def get_tasks(db: Session, owner_username: str):
    user = db.query(User).filter(User.username == owner_username).first()
    if not user:
        return []
    return db.query(Tasks).filter(Tasks.owner_id == user.id).all()


def get_one(db: Session, taskid: int, owner_username: str):
    user = db.query(User).filter(User.username == owner_username).first()
    if not user:
        return None
    return db.query(Tasks).filter(Tasks.id == taskid, Tasks.owner_id == user.id).first()


def update_task_db(data, id, db: Session, owner_username: str):
    user = db.query(User).filter(User.username == owner_username).first()
    if not user:
        return None
    t = db.query(Tasks).filter(Tasks.id == id, Tasks.owner_id == user.id).first()
    if t:
        for key, value in data.model_dump(exclude={"id"}).items():
            setattr(t, key, value)
        db.commit()
        db.refresh(t)
    return t


def delete_task(id, db: Session, owner_username: str):
    user = db.query(User).filter(User.username == owner_username).first()
    if not user:
        return None
    q = db.query(Tasks).filter(Tasks.id == id, Tasks.owner_id == user.id).first()
    if q:
        db.delete(q)
        db.commit()
    return q


def signup_user(db: Session, username: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    user_instance = User(username=username, email=email, password=hashed_password)
    db.add(user_instance)
    db.commit()
    db.refresh(user_instance)
    return user_instance


def start_signup_otp(db: Session, username: str, email: str, password: str):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    code = otp_send(email)
    pending_otps[email] = {
        "username": username,
        "password": password,
        "otp": code,
    }
    return {"message": "OTP sent to the provided email address"}


def verify_otp(db: Session, email: str, otp: int):
    pending = pending_otps.get(email)
    if not pending:
        raise HTTPException(status_code=400, detail="No pending OTP request found for this email")
    if pending["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    created_user = signup_user(db, pending["username"], email, pending["password"])
    del pending_otps[email]
    return created_user


def otp_send(email: str):
    msg = EmailMessage()
    msg["Subject"] = "OTP for Task Manager signup"
    msg["From"] = os.getenv("gmail")
    msg["To"] = email
    code = random.randint(1000, 9999)
    msg.set_content(f"Your verification code is: {code}")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(os.getenv("gmail"), os.getenv("gmail_password"))
    server.send_message(msg)
    server.quit()
    return code


def login_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
