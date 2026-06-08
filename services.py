import os
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError, ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import get_db
from dotenv import load_dotenv
from models import Tasks, User
from schemas import Taskcreate

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

pending_otps: dict[str, dict] = {}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # PyJWT expects a numeric timestamp for exp or a datetime; we pass datetime
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"})
    except PyJWTError:
        raise credentials_exception
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


def create_tasks(db: Session, data: Taskcreate, owner_id: int):
    task_data = data.model_dump(exclude={"id"})
    task_instance = Tasks(**task_data, owner_id=owner_id)
    db.add(task_instance)
    db.commit()
    db.refresh(task_instance)
    return task_instance


def get_tasks(db: Session, owner_id: int):
    return db.query(Tasks).filter(Tasks.owner_id == owner_id).all()


def get_one(db: Session, taskid: int, owner_id: int):
    return db.query(Tasks).filter(Tasks.id == taskid, Tasks.owner_id == owner_id).first()


def update_task_db(data, id, db: Session, owner_id: int):
    t = db.query(Tasks).filter(Tasks.id == id, Tasks.owner_id == owner_id).first()
    if t:
        for key, value in data.model_dump(exclude={"id"}).items():
            setattr(t, key, value)
        db.commit()
        db.refresh(t)
    return t


def delete_task(id, db: Session, owner_id: int):
    q = db.query(Tasks).filter(Tasks.id == id, Tasks.owner_id == owner_id).first()
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

