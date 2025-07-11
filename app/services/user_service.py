# Service functions for user authentication and management
from sqlalchemy.orm import Session
from app.db import crud
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token, get_password_hash
from datetime import datetime, timedelta


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user by email and password.
    Handles account lockout after multiple failed attempts.
    Resets counters on success.
    """
    user = crud.get_user_by_email(db, email)
    if not user:
        return None
    now = datetime.utcnow()
    lockout_until = getattr(user, 'lockout_until', None)
    if lockout_until and lockout_until > now:
        return None  # Account is locked
    if not verify_password(password, user.hashed_password):
        failed_attempts = getattr(user, 'failed_login_attempts', 0) or 0
        user.failed_login_attempts = failed_attempts + 1
        if user.failed_login_attempts >= 5:
            user.lockout_until = now + timedelta(minutes=15)
            user.failed_login_attempts = 0
        db.commit()
        return None
    # Success: reset counters
    user.failed_login_attempts = 0
    user.lockout_until = None
    db.commit()
    return user


def issue_tokens(db: Session, user):
    """
    Issue a new access token and refresh token for a user.
    Stores the refresh token in the database.
    """
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    payload = verify_token(refresh_token)
    expires_at = datetime.utcfromtimestamp(payload["exp"]) if payload and "exp" in payload else datetime.utcnow() + timedelta(days=7)
    crud.create_refresh_token(db, user.id, refresh_token, expires_at)
    return access_token, refresh_token


def validate_and_rotate_refresh_token(db: Session, refresh_token: str):
    """
    Validate a refresh token, rotate it (delete old, issue new), and return new tokens.
    """
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


def change_user_password(db: Session, user, old_password: str, new_password: str):
    """
    Change the user's password after verifying the old password.
    Returns True on success, False if old password is incorrect.
    """
    if not verify_password(old_password, user.hashed_password):
        return False
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return True 