from sqlalchemy.orm import Session
from app.db import crud
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token
from datetime import datetime, timedelta


def authenticate_user(db: Session, email: str, password: str):
    user = crud.get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def issue_tokens(db: Session, user):
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    payload = verify_token(refresh_token)
    expires_at = datetime.utcfromtimestamp(payload["exp"]) if payload and "exp" in payload else datetime.utcnow() + timedelta(days=7)
    crud.create_refresh_token(db, user.id, refresh_token, expires_at)
    return access_token, refresh_token


def validate_and_rotate_refresh_token(db: Session, refresh_token: str):
    payload = verify_token(refresh_token)
    if not payload:
        return None, None
    db_token = crud.get_refresh_token(db, refresh_token)
    # Ensure expires_at is a datetime, not a SQLAlchemy column
    expires_at = getattr(db_token, "expires_at", None)
    if db_token is None or expires_at is None or (isinstance(expires_at, datetime) and expires_at < datetime.utcnow()):
        return None, None
    # Find user by id from db_token
    user = db.query(crud.models.User).filter(crud.models.User.id == db_token.user_id).first()
    if not user:
        return None, None
    # Rotate: delete old, issue new
    crud.delete_refresh_token(db, refresh_token)
    return issue_tokens(db, user) 