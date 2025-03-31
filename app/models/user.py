"""
Database models for users and tokens
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class SuperAdmin(Base):
    """
    SuperAdmin model for admin users who can manage tokens
    """
    __tablename__ = "superadmins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class APIToken(Base):
    """
    API Token model for API authentication
    """
    __tablename__ = "api_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now()) 