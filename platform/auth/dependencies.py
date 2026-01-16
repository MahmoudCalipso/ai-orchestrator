"""
FastAPI Authentication Dependencies
Dependency injection for authentication and authorization
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from .jwt_manager import JWTManager
from .models import User, APIKey
from .rbac import Role, Permission, RBACManager
from platform.tenancy.models import Tenant


# Security scheme
security = HTTPBearer()

# JWT Manager instance
jwt_manager = JWTManager()


def get_db():
    """
    Get database session
    TODO: Replace with actual database session factory
    """
    # This is a placeholder - implement actual DB session management
    pass


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = jwt_manager.verify_token(credentials.credentials, token_type="access")
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user from token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify API key and return associated user
    
    Args:
        x_api_key: API key from header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Hash the provided API key
    key_hash = jwt_manager.hash_api_key(x_api_key)
    
    # Find API key in database
    api_key = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check expiration
    from datetime import datetime
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )
    
    # Update last used
    api_key.last_used = datetime.utcnow()
    api_key.usage_count += 1
    db.commit()
    
    # Get user
    user = db.query(User).filter(User.id == api_key.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


def require_permission(required_permission: Permission):
    """
    Dependency factory to require specific permission
    
    Args:
        required_permission: Permission required
        
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        user_role = Role(current_user.role)
        
        if not RBACManager.check_permission(user_role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {required_permission.value}"
            )
        
        return current_user
    
    return permission_checker


def require_role(required_role: Role):
    """
    Dependency factory to require specific role
    
    Args:
        required_role: Role required
        
    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        user_role = Role(current_user.role)
        
        # Admin has access to everything
        if user_role == Role.ADMIN:
            return current_user
        
        # Check if user's role is sufficient
        role_hierarchy = {
            Role.FREE: 0,
            Role.DEVELOPER: 1,
            Role.PRO: 2,
            Role.ADMIN: 3
        }
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 999):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {required_role.value}"
            )
        
        return current_user
    
    return role_checker


async def get_current_tenant(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Get current user's tenant
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Tenant object
        
    Raises:
        HTTPException: If tenant not found or inactive
    """
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is inactive"
        )
    
    return tenant
