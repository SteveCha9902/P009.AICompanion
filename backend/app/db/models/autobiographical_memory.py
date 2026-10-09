import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from app.db.base import Base

class EpisodicMemoryModel(Base):
    __tablename__ = "episodic_memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False, default="default_user")
    companion_id = Column(String(50), index=True, nullable=False, default="default_companion")
    conversation_id = Column(String(50), nullable=True)
    interaction_id = Column(String(50), nullable=True)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text, nullable=False)
    emotional_context = Column(JSON, default=dict)
    importance = Column(Float, default=0.5, nullable=False)
    event_type = Column(String(50), default="CONVERSATION_EPISODE")
    created_at = Column(DateTime, default=datetime.utcnow)

class LifeEventModel(Base):
    __tablename__ = "life_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False, default="default_user")
    companion_id = Column(String(50), index=True, nullable=False, default="default_companion")
    title = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    category = Column(String(50), default="PROJECT_MILESTONE", nullable=False)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    importance = Column(Float, default=0.8, nullable=False)
    emotional_weight = Column(Float, default=0.7, nullable=False)
    relationship_significance = Column(Float, default=0.7, nullable=False)
    source_episode_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class SharedExperienceModel(Base):
    __tablename__ = "shared_experiences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False, default="default_user")
    companion_id = Column(String(50), index=True, nullable=False, default="default_companion")
    title = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_referenced_at = Column(DateTime, default=datetime.utcnow)
    companion_involvement_level = Column(Float, default=0.8, nullable=False)
    is_co_experienced = Column(Boolean, default=True, nullable=False)
    related_life_event_ids = Column(JSON, default=list)
    importance = Column(Float, default=0.85, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TimelineEventModel(Base):
    __tablename__ = "timeline_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False, default="default_user")
    companion_id = Column(String(50), index=True, nullable=False, default="default_companion")
    occurred_at = Column(DateTime, default=datetime.utcnow)
    title = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    importance = Column(Float, default=0.8, nullable=False)
    event_type = Column(String(50), default="MILESTONE", nullable=False)
    related_event_ids = Column(JSON, default=list)
    story_chapter_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class StoryChapterModel(Base):
    __tablename__ = "story_chapters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), index=True, nullable=False, default="default_user")
    companion_id = Column(String(50), index=True, nullable=False, default="default_companion")
    chapter_number = Column(Integer, default=1, nullable=False)
    title = Column(String(100), nullable=False)
    theme = Column(String(100), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=False)
    importance = Column(Float, default=0.9, nullable=False)
    event_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
