from sqlalchemy.orm import Session
from app.db import crud
from app.core.security import verify_password


def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 