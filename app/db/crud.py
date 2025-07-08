from sqlalchemy.orm import Session
from app.db import models
from app.core.security import get_password_hash, verify_password

# Get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Create a new user with hashed password
def create_user(db: Session, email: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = models.User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Create a new refresh token for a user
def create_refresh_token(db: Session, user_id: int, token: str, expires_at):
    db_token = models.RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

# Get a refresh token by its string value
def get_refresh_token(db: Session, token: str):
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()

# Delete a refresh token (revoke)
def delete_refresh_token(db: Session, token: str):
    db_token = get_refresh_token(db, token)
    if db_token:
        db.delete(db_token)
        db.commit() 