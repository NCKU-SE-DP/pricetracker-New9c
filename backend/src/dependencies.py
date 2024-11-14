from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session
from .database import get_database

DatabaseSession = Annotated[Session, Depends(get_database)]
