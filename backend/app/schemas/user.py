"""
User Schemas - Request/Response validation
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# Base schemas
class UserBase(BaseModel):
    email: EmailStr


# Request schemas
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class TokenRefresh(BaseModel):
    refresh_token: str


# Response schemas
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
