from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.models import User
from .config import configuration
from .exceptions import InvalidCredentialsError

import logging
from sentry_sdk import capture_exception

_pwd_context = CryptContext(schemes=[configuration.password_hashing_algorithm], deprecated="auto")

def _hash_password(original_pwd: str) -> str:
    return _pwd_context.hash(original_pwd)

def _is_pwd_ok(inserted_pwd, hashed_pwd)-> bool: #check if inserted password == hashed password
    return _pwd_context.verify(inserted_pwd, hashed_pwd)


def _check_user_password_is_correct(db, username, pwd)-> User:
    user = db.query(User).filter(User.username == username).first()
    if user is None or not _is_pwd_ok(pwd, user.hashed_password):
        logging.error("Error: Invalid Credentials")
        raise InvalidCredentialsError
    return user


def _create_access_token(data, expires_delta=None)-> str:
    """create access token"""
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + configuration.access_token_valid_duration
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, key=configuration.access_token_secret_key, algorithm=configuration.access_token_algorithm)
    except Exception as e:
        logging.error(f"Error occurred while encode with jwt: {e}")
        raise e
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
