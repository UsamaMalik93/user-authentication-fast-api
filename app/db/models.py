from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import mapped_column
from app.db.base import Base

# User model for authentication and profile
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # Unique user ID
    email = Column(String, unique=True, index=True, nullable=False)  # User email
    hashed_password = Column(String, nullable=False)  # Hashed password
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Registration time
    failed_login_attempts = mapped_column(Integer, default=0)  # Failed login attempts counter
    lockout_until = mapped_column(DateTime(timezone=True), nullable=True)  # Lockout expiry timestamp

# Model for storing refresh tokens
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)  # Unique token ID
    user_id = Column(Integer, nullable=False, index=True)  # Associated user ID
    token = Column(String, unique=True, nullable=False, index=True)  # The refresh token string
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Token creation time
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Token expiry time 