"""
Authentication API Routes
User registration, login, token management, and API keys
"""

import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .schemas import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    TokenResponse,
    UserResponse,
    TenantResponse,
    MeResponse,
    APIKeyCreate,
    APIKeyResponse,
    PasswordChange,
)
from .models import User, APIKey
from .jwt_manager import JWTManager
from .dependencies import get_db, get_current_active_user, get_current_tenant
from .rbac import Role, RBACManager
from platform.tenancy.models import Tenant


router = APIRouter(prefix="/api/v2/auth", tags=["Authentication"])
jwt_manager = JWTManager()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user and create tenant
    
    Creates a new user account with associated tenant.
    Default plan is 'free' with basic quotas.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create tenant
    tenant_id = str(uuid.uuid4())
    tenant = Tenant(
        id=tenant_id,
        name=user_data.tenant_name,
        plan="free",
        storage_quota_gb=10,
        workbench_quota=3,
        api_rate_limit=100
    )
    db.add(tenant)
    
    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = jwt_manager.hash_password(user_data.password)
    
    user = User(
        id=user_id,
        tenant_id=tenant_id,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=Role.FREE.value,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate tokens
    access_token = jwt_manager.create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "tenant_id": tenant_id
    })
    
    refresh_token = jwt_manager.create_refresh_token(user.id, tenant_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=jwt_manager.access_token_expire * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    
    Returns access and refresh tokens for authenticated requests.
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not jwt_manager.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Generate tokens
    access_token = jwt_manager.create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id
    })
    
    refresh_token = jwt_manager.create_refresh_token(user.id, user.tenant_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=jwt_manager.access_token_expire * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    Generates a new access token without requiring re-authentication.
    """
    try:
        # Verify refresh token
        payload = jwt_manager.verify_token(token_data.refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Generate new access token
        access_token = jwt_manager.create_access_token({
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "tenant_id": tenant_id
        })
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=token_data.refresh_token,  # Return same refresh token
            expires_in=jwt_manager.access_token_expire * 60
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout current user
    
    Revokes all refresh tokens for the user.
    """
    jwt_manager.revoke_token(current_user.id)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get current user information
    
    Returns user profile, tenant info, and permissions.
    """
    # Get user permissions
    user_role = Role(current_user.role)
    permissions = [p.value for p in RBACManager.get_role_permissions(user_role)]
    
    return MeResponse(
        user=UserResponse.from_orm(current_user),
        tenant=TenantResponse(
            id=tenant.id,
            name=tenant.name,
            plan=tenant.plan,
            storage_quota_gb=tenant.storage_quota_gb,
            storage_used_gb=tenant.storage_used_gb,
            storage_usage_percent=tenant.storage_usage_percent,
            workbench_quota=tenant.workbench_quota,
            api_rate_limit=tenant.api_rate_limit,
            is_active=tenant.is_active,
            created_at=tenant.created_at
        ),
        permissions=permissions
    )


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key
    
    Generates a new API key for programmatic access.
    The key is only shown once during creation.
    """
    # Generate API key
    api_key = jwt_manager.generate_api_key()
    key_hash = jwt_manager.hash_api_key(api_key)
    
    # Calculate expiration
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Create API key record
    api_key_record = APIKey(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        key_hash=key_hash,
        name=key_data.name,
        expires_at=expires_at,
        is_active=True
    )
    
    db.add(api_key_record)
    db.commit()
    db.refresh(api_key_record)
    
    # Return response with actual key (only time it's shown)
    return APIKeyResponse(
        id=api_key_record.id,
        name=api_key_record.name,
        key=api_key,  # Only returned on creation
        created_at=api_key_record.created_at,
        expires_at=api_key_record.expires_at,
        last_used=None,
        usage_count=0,
        is_active=True
    )


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for current user
    
    Returns list of API keys without the actual key values.
    """
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    
    return [
        APIKeyResponse(
            id=key.id,
            name=key.name,
            key=None,  # Never return actual key
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used=key.last_used,
            usage_count=key.usage_count,
            is_active=key.is_active
        )
        for key in api_keys
    ]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an API key
    
    Deactivates the specified API key.
    """
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    db.commit()
    
    return {"message": "API key revoked successfully"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    Requires current password for verification.
    """
    # Verify current password
    if not jwt_manager.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = jwt_manager.hash_password(password_data.new_password)
    db.commit()
    
    # Revoke all refresh tokens (force re-login on all devices)
    jwt_manager.revoke_token(current_user.id)
    
    return {"message": "Password changed successfully. Please login again."}
