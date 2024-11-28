from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.dependencies import DatabaseSession
from . import service
from .dependencies import CurrentLoggedInUser
from .schemas import UserAuthSchema  


router = APIRouter(prefix="/api/v1/users")
@router.post("/login")
async def login_for_access_token(
        db: DatabaseSession,
        form_data: OAuth2PasswordRequestForm = Depends(),
):
    """login"""
    access_token = service.login(db, form_data.username, form_data.password)
    return access_token

@router.post("/register")
def create_user(user: UserAuthSchema, db: DatabaseSession):
    """create user"""
    db_user = service.register_user(db, user.username, user.password)
    return db_user


@router.get("/me")
def read_users_me(user: CurrentLoggedInUser):
    return {"username": user.username}


