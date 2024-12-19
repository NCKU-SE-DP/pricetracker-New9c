from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError, JWTClaimsError
from src.dependencies import DatabaseSession
from src.models import User
from .config import configuration
from .exceptions import InvalidAccessTokenError

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl=configuration.access_token_url)

def _authenticate_user_token(db: DatabaseSession, token = Depends(_oauth2_scheme)):
    try:
        claims = jwt.decode(token, key=configuration.access_token_secret_key, algorithms=[configuration.access_token_algorithm])
    except (ExpiredSignatureError, JWTClaimsError, JWTError):
        raise InvalidAccessTokenError
    user = db.query(User).filter(User.username == claims.get("sub")).first()
    if user is None:
        raise InvalidAccessTokenError
    return user


CurrentLoggedInUser = Annotated[User, Depends(_authenticate_user_token)]

