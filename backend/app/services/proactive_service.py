from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone, timedelta
from app.db.models.proactive import ProactiveEvent, ProactiveSettings, ProactiveTriggerType, ProactiveDecision
from app.db.models.relationship import RelationshipLevel, RelationshipState
from app.db.models.presence import PresenceState, PresenceStateEnum
from app.repositories.proactive_repository import ProactiveRepository
import logging

logger = logging.getLogger(__name__)

class ProactivePolicyEngine:
    def __init__(self, repo: ProactiveRepository):
        self.repo = repo

    async def evaluate_eligibility(
        self,
        companion_id: str,
        presence: PresenceState,
        relationship: RelationshipState,
        trigger: ProactiveTriggerType,
        memory_context_count: int = 0
    ) -> Tuple[ProactiveDecision, float, str]:
        """
        Evaluates whether a proactive message should be ALLOWED or DENIED.
        Returns: (Decision, Score, Reason)
        """
        settings = await self.repo.get_settings(companion_id)
        now = datetime.now(timezone.utc)
        
        # 1. Master Switch Check
        if not settings.enabled:
            return ProactiveDecision.DENY, 0.0, "Proactive interaction is disabled by user."
            
        # 2. Presence Check
        if presence.state in (PresenceStateEnum.OFFLINE, PresenceStateEnum.SLEEPING, PresenceStateEnum.ENGAGED):
            return ProactiveDecision.DENY, 0.0, f"Companion presence is {presence.state}, cannot interrupt."

        # 3. Quiet Hours Check
        current_time_str = now.strftime("%H:%M")
        if self._is_quiet_hours(current_time_str, settings.quiet_hours_start, settings.quiet_hours_end):
            return ProactiveDecision.DENY, 0.0, "Currently in quiet hours."

        # 4. Daily Limit Check
        recent_events = await self.repo.get_recent_events(companion_id, limit=50)
        daily_count = sum(1 for e in recent_events if e.decision == ProactiveDecision.ALLOW and e.created_at.date() == now.date())
        if daily_count >= settings.daily_limit:
            return ProactiveDecision.DENY, 0.0, f"Daily limit ({settings.daily_limit}) reached."

        # 5. Cooldown Check
        last_allow = next((e for e in recent_events if e.decision == ProactiveDecision.ALLOW), None)
        if last_allow:
            minutes_since = (now - last_allow.created_at.replace(tzinfo=timezone.utc)).total_seconds() / 60
            if minutes_since < settings.cooldown_minutes:
                return ProactiveDecision.DENY, 0.0, f"In cooldown period ({minutes_since:.1f}m < {settings.cooldown_minutes}m)."

        # 6. Base Score Calculation
        score = 0.5  # Base
        
        # Relationship Modifiers
        if relationship.relationship_level == RelationshipLevel.STRANGER:
            # Prevent most proactive interactions with strangers unless they just returned
            if trigger != ProactiveTriggerType.RETURNED_USER:
                return ProactiveDecision.DENY, 0.2, "Relationship is too low (STRANGER) to initiate casual conversation."
        elif relationship.relationship_level in (RelationshipLevel.CLOSE, RelationshipLevel.TRUSTED):
            score += 0.2
            
        # Trigger Specific Rules
        if trigger == ProactiveTriggerType.LONG_ABSENCE:
            if not presence.last_interaction_at:
                return ProactiveDecision.DENY, 0.1, "No previous interaction."
                
            days_absent = (now - presence.last_interaction_at.replace(tzinfo=timezone.utc)).total_seconds() / (60 * 60 * 24)
            if days_absent < 2:
                return ProactiveDecision.DENY, 0.3, "Absence not long enough for this trigger."
            
            score += min(0.3, days_absent * 0.05)
            
        elif trigger == ProactiveTriggerType.TIME_BASED:
            # Time-based triggers require high relationship and a reason (like memory)
            if relationship.relationship_level not in (RelationshipLevel.CLOSE, RelationshipLevel.TRUSTED):
                return ProactiveDecision.DENY, 0.3, "Time-based triggers require CLOSE relationship."
            if memory_context_count == 0:
                return ProactiveDecision.DENY, 0.3, "Time-based triggers require relevant memory context to prevent spam."
            score += 0.1
            
        # Memory Context
        if memory_context_count > 0:
            score += 0.2
            
        # 7. Final Threshold Check
        THRESHOLD = 0.6
        if score >= THRESHOLD:
            return ProactiveDecision.ALLOW, score, "Score met threshold based on relationship and context."
        else:
            return ProactiveDecision.DENY, score, f"Score {score:.2f} did not meet threshold {THRESHOLD}."
            
    def _is_quiet_hours(self, current: str, start: str, end: str) -> bool:
        """Simple time string comparison. HH:MM"""
        # E.g., start 23:00, end 07:00
        if start > end:
            return current >= start or current <= end
        return start <= current <= end

class ProactiveService:
    def __init__(self, repo: ProactiveRepository, policy_engine: ProactivePolicyEngine):
        self.repo = repo
        self.policy_engine = policy_engine

    async def evaluate_and_log_trigger(
        self,
        companion_id: str,
        presence: PresenceState,
        relationship: RelationshipState,
        trigger: ProactiveTriggerType,
        source: str,
        memory_ids: List[str] = None
    ) -> ProactiveEvent:
        """
        Evaluates a trigger and logs the event. Returns the event so the caller can check `event.decision`.
        """
        mem_count = len(memory_ids) if memory_ids else 0
        decision, score, reason = await self.policy_engine.evaluate_eligibility(
            companion_id=companion_id,
            presence=presence,
            relationship=relationship,
            trigger=trigger,
            memory_context_count=mem_count
        )
        
        event = ProactiveEvent(
            companion_id=companion_id,
            trigger_type=trigger,
            trigger_source=source,
            decision=decision,
            score=score,
            decision_reason=reason,
            selected_memory_ids=memory_ids or [],
            relationship_snapshot={
                "level": relationship.relationship_level.value if hasattr(relationship.relationship_level, 'value') else str(relationship.relationship_level),
                "trust": relationship.trust,
                "closeness": relationship.closeness
            }
        )
        
        return await self.repo.log_event(event)

