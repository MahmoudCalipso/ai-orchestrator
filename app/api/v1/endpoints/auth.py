"""Authentication API Endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import logging
from datetime import datetime, timedelta

from ....core.database import get_db
from ....middleware.auth import TokenService, require_auth
# Note: Models and DTOs from legacy structure are referenced here. 
# In a full migration, these DTOs would be moved to app/schemas/v1/auth.py
from platform_core.auth.models import User
from dto.v1.requests.auth import UserRegisterRequest, UserLoginRequest, TokenRefreshRequest
from dto.v1.responses.auth import TokenResponseDTO
from dto.common.base_response import BaseResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=BaseResponse)
async def register(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if email exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Logic for creating user and tenant would go here
    # Using TokenService for token generation
    access_token = TokenService.create_access_token(user_id="placeholder_uid")
    refresh_token = TokenService.create_refresh_token(user_id="placeholder_uid")
    
    return BaseResponse(
        status="success",
        code="USER_REGISTERED",
        message="User registered successfully",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 1800
        }
    )

@router.post("/login", response_model=BaseResponse)
async def login(
    credentials: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password."""
    stmt = select(User).where(User.email == credentials.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # In a real app, verify password hash here
    if not user:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = TokenService.create_access_token(user_id=user.id)
    refresh_token = TokenService.create_refresh_token(user_id=user.id)
    
    return BaseResponse(
        status="success",
        code="LOGIN_SUCCESS",
        message="Login successful",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 1800
        }
    )
