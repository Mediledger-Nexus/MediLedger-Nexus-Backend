"""
Health Vault model for MediLedger Nexus
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from mediledger_nexus.core.database import Base


class HealthVault(Base):
    """Health Vault model for storing encrypted medical data"""
    
    __tablename__ = "health_vaults"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Vault metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Blockchain and encryption
    hedera_topic_id = Column(String(50), nullable=True)  # HCS topic for vault events
    ipfs_hash = Column(String(100), nullable=True)  # IPFS hash for vault metadata
    encryption_key_hash = Column(String(255), nullable=False)  # Hash of encryption key
    
    # Configuration
    encryption_enabled = Column(Boolean, default=True)
    zk_proofs_enabled = Column(Boolean, default=True)
    emergency_access_enabled = Column(Boolean, default=True)
    
    # Statistics
    total_records = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    access_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="health_vaults")
    medical_records = relationship("MedicalRecord", back_populates="vault", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="vault", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<HealthVault(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
    
    @property
    def is_encrypted(self) -> bool:
        return self.encryption_enabled
    
    @property
    def supports_zk_proofs(self) -> bool:
        return self.zk_proofs_enabled
