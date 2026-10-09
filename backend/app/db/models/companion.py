from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class Companion(Base):
    __tablename__ = "companions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String, nullable=False, default="Luna")
    
    # SB-5 Lifecycle Management
    lifecycle_status = Column(String(20), default="available", nullable=False) # 'available', 'archived', 'deleted'
    is_system_character = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="companion")
    persona = relationship("Persona", back_populates="companion", uselist=False, cascade="all, delete-orphan")
