"""
Authentication Database Models
User, APIKey, and related models
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from platform_core.database import Base, SessionLocal





class User(Base):
    """User model with tenant association"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="developer", index=True)  # admin, enterprise, pro_developer, developer
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    credentials_accepted = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    external_accounts = relationship("ExternalAccount", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class APIKey(Base):
    """API Key model for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    key_hash = Column(String, nullable=False, unique=True)
    name = Column(String)
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey {self.name} for user {self.user_id}>"


class RefreshToken(Base):
    """Refresh token storage for token rotation"""
    __tablename__ = "refresh_tokens"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    revoked = Column(Boolean, default=False, index=True)
    revoked_at = Column(DateTime)
    
    def __repr__(self):
        return f"<RefreshToken for user {self.user_id}>"


class ExternalAccount(Base):
    """External account linkage (GitHub, Google, etc)"""
    __tablename__ = "external_accounts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String, nullable=False)  # github, bitbucket, gitlab, google
    provider_user_id = Column(String, nullable=False)
    
    # Encrypted tokens
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    token_type = Column(String, default="Bearer")
    
    expires_at = Column(DateTime)
    username = Column(String)
    email = Column(String)
    avatar_url = Column(String)
    
    # JSON list of granted scopes Stored as JSON string
    scopes = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="external_accounts")
    
    def __repr__(self):
        return f"<ExternalAccount {self.provider}:{self.username} for user {self.user_id}>"


class PasswordResetToken(Base):
    """Secure tokens for password reset flow"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    used = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<PasswordResetToken for user {self.user_id}>"
