from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from src.dependencies import DatabaseSession
from src.models import User
from typing import Annotated
from .config import configuration

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl=configuration.access_token_url)

def _authenticate_user_token(db: DatabaseSession, token = Depends(_oauth2_scheme)):
    payload = jwt.decode(token, key=configuration.access_token_secret_key, algorithms=configuration.access_token_algorithm)
    return db.query(User).filter(User.username == payload.get("sub")).first()


CurrentLoggedInUser = Annotated[User, Depends(_authenticate_user_token)]

