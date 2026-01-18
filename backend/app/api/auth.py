"""
Authentication API Routes
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, 
    create_access_token, create_refresh_token, decode_token,
    get_current_user
)
from app.core.config import settings
from app.models.user import User
from app.models.profile import Profile
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, 
    TokenResponse, AuthResponse, TokenRefresh
)


router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.flush()
    
    # Create empty profile
    profile = Profile(
        user_id=user.id,
        first_name="",
        last_name="",
    )
    db.add(profile)
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    tokens = _create_tokens(user)
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with email and password"""
    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    tokens = _create_tokens(user)
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token"""
    payload = decode_token(data.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    return _create_tokens(user)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


def _create_tokens(user: User) -> TokenResponse:
    """Create access and refresh tokens"""
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
