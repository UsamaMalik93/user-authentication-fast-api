from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest
from app.db import crud
from app.services.user_service import authenticate_user, issue_tokens, validate_and_rotate_refresh_token
from app.api.deps import get_db
from app.core.security import create_access_token
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, user_in.email, user_in.password)
    return user

@router.post("/login", response_model=TokenResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token, refresh_token = issue_tokens(db, user)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    access_token, refresh_token = validate_and_rotate_refresh_token(db, request.refresh_token)
    if not access_token or not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout")
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    crud.delete_refresh_token(db, request.refresh_token)
    return {"msg": "Logged out successfully."}

@router.get("/me", response_model=UserResponse)
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = crud.get_user_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user 