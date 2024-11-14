from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.models import User
from .config import configuration

_pwd_context = CryptContext(schemes=[configuration.password_hashing_algorithm], deprecated="auto")

def _hash_password(original_pwd: str) -> str:
    return _pwd_context.hash(original_pwd)

def _verify(inserted_pwd, hashed_pwd)-> bool: #check if inserted password == hashed password
    return _pwd_context.verify(inserted_pwd, hashed_pwd)


def _check_user_password_is_correct(db, username, pwd)-> User|None:
    user = db.query(User).filter(User.username == username).first()
    if not _verify(pwd, user.hashed_password):
        return None
    return user


def _create_access_token(data, expires_delta=None)-> str:
    """create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=configuration.access_token_valid_duration)
    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, key=configuration.access_token_secret_key, algorithm=configuration.access_token_algorithm)
    return encoded_jwt


def login(db: Session, username: str, password: str) -> dict: 
    user = _check_user_password_is_correct(db, username, password)
    access_token = _create_access_token(
        data={"sub": str(user.username)}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

def register_user(db: Session, username: str, password: str) -> User:
    hashed_password = _hash_password(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
