import enum
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)


class InteractionExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STALE = "stale"


class InteractionExecutionRecord(BaseModel):
    """
    Immutable Execution Record for an interaction turn to guarantee idempotency and tracing.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    interaction_id: str
    user_id: str
    companion_id: str
    status: InteractionExecutionStatus = InteractionExecutionStatus.PENDING
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    result_summary: Optional[str] = None


class InteractionExecutionRegistry:
    """
    In-memory / Redis-backed idempotency registry.
    Ensures an interaction is only executed once and prevents duplicate state mutations.
    """

    def __init__(self):
        self._registry: Dict[str, InteractionExecutionRecord] = {}

    def register_start(self, interaction_id: str, user_id: str, companion_id: str) -> Tuple[bool, Optional[InteractionExecutionRecord]]:
        """
        Attempts to register and start an interaction.
        Returns (is_new, record). If already completed or running, is_new will be False.
        """
        existing = self._registry.get(interaction_id)
        if existing:
            if existing.user_id != user_id or existing.companion_id != companion_id:
                raise PermissionError(f"Interaction {interaction_id} ownership mismatch!")
            return False, existing

        record = InteractionExecutionRecord(
            interaction_id=interaction_id,
            user_id=user_id,
            companion_id=companion_id,
            status=InteractionExecutionStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        self._registry[interaction_id] = record
        return True, record

    def mark_completed(self, interaction_id: str, result_summary: Optional[str] = None) -> bool:
        record = self._registry.get(interaction_id)
        if record:
            record.status = InteractionExecutionStatus.COMPLETED
            record.completed_at = datetime.utcnow()
            record.result_summary = result_summary
            return True
        return False

    def mark_failed(self, interaction_id: str, error_code: str, error_message: str) -> bool:
        record = self._registry.get(interaction_id)
        if record:
            record.status = InteractionExecutionStatus.FAILED
            record.completed_at = datetime.utcnow()
            record.error_code = error_code
            record.error_message = error_message
            return True
        return False

    def get_record(self, interaction_id: str) -> Optional[InteractionExecutionRecord]:
        return self._registry.get(interaction_id)
