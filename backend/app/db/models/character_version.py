import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base


class CharacterVersionModel(Base):
    """
    Stores historical snapshots of Character DNA upon evolution/updates.
    Enables audit trail, rollback, and identity progression tracking.
    """
    __tablename__ = "character_versions"
    __table_args__ = (
        UniqueConstraint("companion_id", "version", name="uq_character_version"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String(50), ForeignKey("companions.id"), index=True, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    dna_snapshot = Column(JSON, nullable=False)
    change_type = Column(String(20), nullable=False, default="minor") # 'initial', 'cosmetic', 'minor', 'major'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
