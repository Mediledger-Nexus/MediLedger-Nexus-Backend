"""
User model for MediLedger Nexus
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from mediledger_nexus.core.database import Base


class User(Base):
    """User model for patients, healthcare providers, and researchers"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Hedera blockchain account
    hedera_account_id = Column(String(50), nullable=True, index=True)
    hedera_public_key = Column(Text, nullable=True)
    
    # User type and status
    user_type = Column(String(50), default="patient")  # patient, provider, researcher, admin
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Emergency information
    emergency_contact = Column(String(255), nullable=True)
    blood_type = Column(String(10), nullable=True)
    allergies = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    health_vaults = relationship("HealthVault", back_populates="owner", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="patient", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="user", cascade="all, delete-orphan")
    ai_agents = relationship("AIAgent", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, type={self.user_type})>"
    
    @property
    def is_patient(self) -> bool:
        return self.user_type == "patient"
    
    @property
    def is_provider(self) -> bool:
        return self.user_type == "provider"
    
    @property
    def is_researcher(self) -> bool:
        return self.user_type == "researcher"
