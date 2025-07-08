# Import FastAPI and dependencies
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# Import schemas for request and response validation
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest, ChangePasswordRequest
# Import CRUD and service logic
from app.db import crud
from app.services.user_service import authenticate_user, issue_tokens, validate_and_rotate_refresh_token, change_user_password
from app.api.deps import get_db
from app.core.security import create_access_token, verify_token
from fastapi.security import OAuth2PasswordBearer

# Create an API router for authentication endpoints
router = APIRouter()
# OAuth2 scheme for extracting the token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# User registration endpoint
@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.
    Returns the created user (without password).
    """
    user = crud.get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, user_in.email, user_in.password)
    return user

# User login endpoint
@router.post("/login", response_model=TokenResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access and refresh tokens.
    """
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token, refresh_token = issue_tokens(db, user)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# Token refresh endpoint
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access and refresh token pair.
    """
    access_token, refresh_token = validate_and_rotate_refresh_token(db, request.refresh_token)
    if not access_token or not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# Logout endpoint
@router.post("/logout")
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Revoke (delete) the provided refresh token, logging the user out.
    """
    crud.delete_refresh_token(db, request.refresh_token)
    return {"msg": "Logged out successfully."}

# Change password endpoint
@router.post("/change-password")
def change_password(request: ChangePasswordRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Change the password for the authenticated user.
    Requires the old password for verification.
    """
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = crud.get_user_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    success = change_user_password(db, user, request.old_password, request.new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")
    return {"msg": "Password changed successfully."}

# Get current user profile endpoint
@router.get("/me", response_model=UserResponse)
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get the profile of the currently authenticated user.
    """
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = crud.get_user_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user 