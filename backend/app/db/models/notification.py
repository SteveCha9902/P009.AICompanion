from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import enum

class NotificationStatus(str, enum.Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    OPENED = "OPENED"
    FAILED = "FAILED"
    DISMISSED = "DISMISSED"

class NotificationEvent(Base):
    __tablename__ = "notification_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
    
    message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    proactive_event_id = Column(String, ForeignKey("proactive_events.id"), nullable=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    
    type = Column(String, nullable=False) # e.g., "PROACTIVE_MESSAGE", "REMINDER"
    channel = Column(String, nullable=False) # e.g., "EXPO", "FCM", "IN_APP"
    
    status = Column(Enum(NotificationStatus), nullable=False, default=NotificationStatus.CREATED)
    
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companion_id = Column(String, ForeignKey("companions.id"), unique=True, index=True, nullable=False)
    
    push_token = Column(String, nullable=True)
    
    notifications_enabled = Column(Boolean, default=True)
    proactive_messages_enabled = Column(Boolean, default=True)
    notification_preview_enabled = Column(Boolean, default=True)
    never_disturb = Column(Boolean, default=False)
    quiet_hours_start = Column(String, default="23:00")
    quiet_hours_end = Column(String, default="07:00")
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
