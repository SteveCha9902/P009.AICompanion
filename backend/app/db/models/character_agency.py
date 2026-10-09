import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text
from app.db.base import Base

class AgencyActionModel(Base):
    """
    Persisted logs of autonomous agency decisions, executions, and blocks.
    """
    __tablename__ = "agency_action_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False, default="default_user")
    companion_id = Column(String(50), index=True, nullable=False, default="genie")
    action_type = Column(String(50), nullable=False, default="STAY_SILENT")
    delivery_channel = Column(String(50), nullable=False, default="NONE")
    priority_score = Column(Float, default=0.0, nullable=False)
    initiative_strength = Column(Float, default=0.0, nullable=False)
    budget_cost = Column(Float, default=0.0, nullable=False)
    decision_status = Column(String(50), default="CREATED", nullable=False)
    blocked_reason = Column(String(100), nullable=True)
    reason = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
