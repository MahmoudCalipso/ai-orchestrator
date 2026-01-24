"""
Authentication API Controller
Handles user registration, login, token management, and API keys.
Converted from legacy platform_core routes.
"""

import uuid
import secrets
import hashlib
import os
import logging
from core.security import verify_api_key, SecurityManager, Role, JWTManager
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from platform_core.auth.dependencies import get_db, get_current_active_user, get_current_tenant
from platform_core.auth import email_service

from platform_core.tenancy.models import Tenant
from platform_core.auth.models import User, APIKey, ExternalAccount, PasswordResetToken
from dto.common.base_response import BaseResponse
from dto.v1.requests.auth import (
    UserRegisterRequest, UserLoginRequest, TokenRefreshRequest,
    APIKeyCreateRequest, PasswordChangeRequest, ForgotPasswordRequest,
    PasswordResetRequest, OAuthConnectRequest
)
from dto.v1.responses.auth import (
    TokenResponseDTO, UserResponseDTO, TenantResponseDTO,
    APIKeyResponseDTO, ExternalAccountResponseDTO, MeResponseDTO
)
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
jwt_manager = JWTManager()


@router.post("/register", response_model=BaseResponse[TokenResponseDTO], status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user and create tenant
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
        role=Role.DEVELOPER.value,
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
    
    return BaseResponse(
        status="success",
        code="USER_REGISTERED",
        message="User registered successfully",
        data=TokenResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=jwt_manager.access_token_expire * 60
        )
    )


@router.post("/login", response_model=BaseResponse[TokenResponseDTO])
async def login(
    credentials: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
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
    
    return BaseResponse(
        status="success",
        code="LOGIN_SUCCESS",
        message="Login successful",
        data=TokenResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=jwt_manager.access_token_expire * 60
        )
    )


@router.post("/refresh", response_model=BaseResponse[TokenResponseDTO])
async def refresh_token(
    token_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
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
        
        return BaseResponse(
            status="success",
            code="TOKEN_REFRESHED",
            message="Token refreshed successfully",
            data=TokenResponseDTO(
                access_token=access_token,
                refresh_token=token_data.refresh_token,
                expires_in=jwt_manager.access_token_expire * 60
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout", response_model=BaseResponse)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout current user
    """
    jwt_manager.revoke_token(current_user.id)
    return BaseResponse(status="success", code="LOGOUT_SUCCESS", message="Successfully logged out")


@router.get("/me", response_model=BaseResponse[MeResponseDTO])
async def get_me(
    current_user: User = Depends(get_current_active_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get current user information
    """
    # Get user permissions
    user_role = Role(current_user.role)
    permissions = [p.value for p in RBACManager.get_role_permissions(user_role)]
    
    # Get external accounts
    external_accounts = db.query(ExternalAccount).filter(ExternalAccount.user_id == current_user.id).all()
    
    return BaseResponse(
        status="success",
        code="ME_RETRIEVED",
        data=MeResponseDTO(
            user=UserResponseDTO.model_validate(current_user),
            tenant=TenantResponseDTO.model_validate(tenant),
            permissions=permissions,
            external_accounts=[ExternalAccountResponseDTO.model_validate(acc) for acc in external_accounts]
        )
    )


@router.get("/external/connect/{provider}")
async def connect_external_account(
    provider: str,
    current_user: User = Depends(get_current_active_user)
):
    """Initiate OAuth2 connection to an external account"""
    state = secrets.token_urlsafe(32)
    redirect_uri = f"{os.getenv('FRONTEND_URL')}/auth/callback/{provider}"
    auth_url = oauth_service.get_auth_url(provider, redirect_uri, state)
    return BaseResponse(
        status="success",
        code="OAUTH_CONNECT_URL",
        data={"auth_url": auth_url, "state": state}
    )


@router.get("/external/callback/{provider}")
async def external_callback(
    provider: str,
    code: str,
    state: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Handle OAuth2 callback and link account"""
    redirect_uri = f"{os.getenv('FRONTEND_URL')}/auth/callback/{provider}"
    
    try:
        # 1. Exchange code for token
        token_data = await oauth_service.exchange_code(provider, code, redirect_uri)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        
        # 2. Get profile
        profile = await oauth_service.get_user_profile(provider, access_token)
        mapped = oauth_service.map_profile(provider, profile)
        
        # 3. Encrypt tokens
        encrypted_access = encryption_service.encrypt(access_token)
        encrypted_refresh = encryption_service.encrypt(refresh_token) if refresh_token else None
        
        # 4. Save or update ExternalAccount
        existing = db.query(ExternalAccount).filter(
            ExternalAccount.user_id == current_user.id,
            ExternalAccount.provider == provider
        ).first()
        
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None
        
        if existing:
            existing.access_token = encrypted_access
            existing.refresh_token = encrypted_refresh
            existing.expires_at = expires_at
            existing.username = mapped["username"]
            existing.avatar_url = mapped["avatar"]
            existing.scopes = json.dumps(token_data.get("scope", "").split(" "))
        else:
            new_acc = ExternalAccount(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                provider=provider,
                provider_user_id=mapped["uid"],
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                expires_at=expires_at,
                username=mapped["username"],
                email=mapped["email"],
                avatar_url=mapped["avatar"],
                scopes=json.dumps(token_data.get("scope", "").split(" "))
            )
            db.add(new_acc)
            
        # 5. Optional: Sync details to User model if missing
        user_updated = False
        if not current_user.full_name and mapped.get("username"):
            current_user.full_name = mapped["username"]
            user_updated = True
        
        if user_updated:
            db.add(current_user)
            
        db.commit()
        return BaseResponse(
            status="success",
            code="OAUTH_ACCOUNT_LINKED",
            message=f"Connected to {provider} successfully"
        )
        
    except Exception as e:
        logger.error(f"OAuth callback failed for {provider}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api-keys", response_model=BaseResponse[APIKeyResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key
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
    
    return BaseResponse(
        status="success",
        code="API_KEY_CREATED",
        message=f"API key '{api_key_record.name}' created",
        data=APIKeyResponseDTO.model_validate({
            "id": api_key_record.id,
            "name": api_key_record.name,
            "key": api_key,
            "created_at": api_key_record.created_at,
            "expires_at": api_key_record.expires_at,
            "usage_count": 0,
            "is_active": True
        })
    )


@router.get("/api-keys", response_model=BaseResponse[List[APIKeyResponseDTO]])
async def list_api_keys(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for current user with search
    """
    query = db.query(APIKey).filter(APIKey.user_id == current_user.id)
    if search:
        query = query.filter(APIKey.name.ilike(f"%{search}%"))
    
    api_keys = query.all()
    
    return BaseResponse(
        status="success",
        code="API_KEYS_RETRIEVED",
        message=f"Retrieved {len(api_keys)} API keys",
        data=[APIKeyResponseDTO.model_validate(key) for key in api_keys],
        meta={"search": search}
    )


@router.delete("/api-keys/{key_id}", response_model=BaseResponse[Dict[str, str]])
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an API key
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
    
    return BaseResponse(
        status="success",
        code="API_KEY_REVOKED",
        message="API key revoked successfully",
        data={"key_id": key_id}
    )


@router.post("/change-password", response_model=BaseResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
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
    
    return BaseResponse(
        status="success",
        code="PASSWORD_CHANGED",
        message="Password changed successfully. Please login again."
    )


@router.post("/accept-credentials", response_model=BaseResponse)
async def accept_credentials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    User acknowledges and accepts Git credentials/terms
    """
    current_user.credentials_accepted = True
    current_user.updated_at = datetime.utcnow()
    db.commit()
    return BaseResponse(status="success", code="CREDENTIALS_ACCEPTED", message="Credentials accepted successfully")


@router.post("/forgot-password", response_model=BaseResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset email
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return BaseResponse(
            status="success",
            code="FORGOT_PASSWORD_SENT",
            message="If this email is registered, you will receive a reset link shortly."
        )
    
    # Generate token
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Save token
    reset_token = PasswordResetToken(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False
    )
    db.add(reset_token)
    db.commit()
    
    # Send email
    await email_service.send_password_reset_email(user.email, token)
    
    return BaseResponse(
        status="success",
        code="FORGOT_PASSWORD_SENT",
        message="If this email is registered, you will receive a reset link shortly."
    )


@router.post("/reset-password", response_model=BaseResponse)
async def reset_password(
    data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using token
    """
    token_hash = hashlib.sha256(data.token.encode()).hexdigest()
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update password
    user.hashed_password = jwt_manager.hash_password(data.new_password)
    reset_token.used = True
    db.commit()
    
    # Revoke all tokens
    jwt_manager.revoke_token(user.id)
    
    return BaseResponse(
        status="success",
        code="PASSWORD_RESET_SUCCESS",
        message="Password reset successfully. Please login with your new password."
    )
