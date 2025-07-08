from pydantic import BaseModel, EmailStr

# Schema for user registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for returning user info (response)
class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

# Schema for access/refresh token response
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Schema for refresh token request
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Schema for change password request
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str 