"""
Database model for CFDI History
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.user import Base


class CFDIHistory(Base):
    """
    CFDI History model to store verification results
    """
    __tablename__ = "cfdi_history"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, nullable=False)
    emisor_rfc = Column(String, nullable=False)
    receptor_rfc = Column(String, nullable=False)
    total = Column(String, nullable=False)
    
    # Verification results
    estado = Column(String, nullable=True)
    es_cancelable = Column(String, nullable=True)
    estatus_cancelacion = Column(String, nullable=True)
    codigo_estatus = Column(String, nullable=True)
    validacion_efos = Column(String, nullable=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="cfdi_history")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 