from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging

from app.db.models.interaction_session import InteractionSession, InteractionSessionState, PendingInteraction
from app.db.models.persona import Persona
from app.db.models.relationship import RelationshipState
from app.db.models.emotion import EmotionState
from app.db.models.conversation import Conversation
from app.db.models.notification import NotificationEvent

logger = logging.getLogger(__name__)

class ContinuityEngine:
    def __init__(self, db: Session):
        self.db = db

    def restore_session(self, companion_id: str, notification_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Orchestrates the Context Restore pipeline upon App Launch or Notification Tap.
        Builds the "Continuity Context" necessary for the Companion to resume naturally.
        """
        logger.info(f"Restoring Continuity for Companion {companion_id} | Notification: {notification_id}")
        
        # 1. Update/Create Interaction Session
        session = self.db.query(InteractionSession)\
            .filter(InteractionSession.companion_id == companion_id)\
            .order_by(InteractionSession.started_at.desc())\
            .first()
            
        if not session or session.state == InteractionSessionState.ENDED:
            session = InteractionSession(companion_id=companion_id, state=InteractionSessionState.ACTIVE)
            self.db.add(session)
        else:
            session.state = InteractionSessionState.ACTIVE
            
        # 2. Check for Notification Context
        notification = None
        if notification_id:
            notification = self.db.query(NotificationEvent).filter(NotificationEvent.id == notification_id).first()
            if notification:
                notification.status = "OPENED" # NotificationStatus.OPENED
                
        # 3. Check for Pending Interactions
        pending_query = self.db.query(PendingInteraction)\
            .filter(PendingInteraction.companion_id == companion_id, PendingInteraction.is_active == True)
        if notification and notification.proactive_event_id:
            pending_query = pending_query.filter(PendingInteraction.proactive_event_id == notification.proactive_event_id)
        
        pending_interaction = pending_query.first()
        
        # 4. Load Core States
        persona = self.db.query(Persona).filter(Persona.companion_id == companion_id).first()
        relationship = self.db.query(RelationshipState).filter(RelationshipState.companion_id == companion_id).first()
        emotion = self.db.query(EmotionState).filter(EmotionState.companion_id == companion_id).first()
        
        # 5. Load Last Conversation
        last_conversation = None
        if notification and notification.conversation_id:
            last_conversation = self.db.query(Conversation).filter(Conversation.id == notification.conversation_id).first()
        else:
            last_conversation = self.db.query(Conversation)\
                .filter(Conversation.companion_id == companion_id)\
                .order_by(Conversation.created_at.desc())\
                .first()

        self.db.commit()

        # 6. Build and Return Continuity Context
        return {
            "session_id": session.id,
            "persona": persona.core_identity if persona else None,
            "relationship_level": relationship.relationship_level.value if relationship else None,
            "emotion": emotion.primary_emotion if emotion else "NEUTRAL",
            "last_conversation_id": last_conversation.id if last_conversation else None,
            "pending_interaction": {
                "intent": pending_interaction.intent,
                "context": pending_interaction.context_data
            } if pending_interaction else None
        }
