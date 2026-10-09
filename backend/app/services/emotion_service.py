import logging
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.emotion import EmotionState, EmotionEvent, EmotionType
from app.repositories.emotion_repository import EmotionRepository
from app.repositories.companion_repository import CompanionRepository
from app.repositories.persona_repository import PersonaRepository
from app.services.emotion.extractor import EmotionExtractor
from app.services.emotion.transition import TransitionEngine
from app.services.emotion.decay import DecayEngine

logger = logging.getLogger(__name__)

class EmotionService:
    def __init__(
        self,
        session: AsyncSession,
        emotion_repo: EmotionRepository,
        companion_repo: CompanionRepository,
        persona_repo: PersonaRepository,
        extractor: EmotionExtractor,
        transition_engine: TransitionEngine,
        decay_engine: DecayEngine
    ):
        self.session = session
        self.emotion_repo = emotion_repo
        self.companion_repo = companion_repo
        self.persona_repo = persona_repo
        self.extractor = extractor
        self.transition_engine = transition_engine
        self.decay_engine = decay_engine

    async def get_current_state(self, companion_id: str) -> EmotionState:
        """
        Retrieves the current state, applying decay if necessary.
        """
        state = await self.emotion_repo.get_state(companion_id)
        if not state:
            # Return default state
            state = EmotionState(companion_id=companion_id)
            state = await self.emotion_repo.save_state(state)
            
        # Apply decay based on current time
        decayed_state = self.decay_engine.apply_decay(state)
        
        # Save the decayed state to DB
        return await self.emotion_repo.save_state(decayed_state)

    async def process_user_message(
        self,
        user_id: str,
        conversation_id: str,
        message_id: str,
        current_message: str,
        history: list,
        companion_id: Optional[str] = None
    ):
        """
        Extracts emotion signal from user message, transitions state, and logs event.
        Supports pinned companion_id for multi-character scope safety.
        """
        try:
            target_companion_id = companion_id
            if not target_companion_id:
                companion = await self.companion_repo.get_by_user_id(user_id)
                if not companion:
                    return
                target_companion_id = companion.id

            # 1. Get current decayed state
            previous_state = await self.get_current_state(target_companion_id)
            
            # 2. Extract Emotion Signal
            signal = await self.extractor.extract_signal(current_message, history)
            if not signal:
                return
                
            intensity = signal.get("intensity", 0.0)
            if intensity < 0.1:
                return # Skip if signal is too weak

            # 3. Get Persona (to influence transition)
            persona = await self.persona_repo.get_by_companion_id(companion.id)
            persona_warmth = 0.5
            if persona and persona.personality:
                persona_warmth = persona.personality.get("warm", 50) / 100.0

            # 4. Transition State
            new_state = self.transition_engine.calculate_transition(
                previous_state=previous_state,
                emotion_signal=signal,
                persona_base_warmth=persona_warmth
            )
            
            # Set new trigger time
            new_state.last_trigger_at = datetime.now(timezone.utc)
            
            # 5. Save New State
            saved_state = await self.emotion_repo.save_state(new_state)
            
            # 6. Log Event
            event = EmotionEvent(
                companion_id=companion.id,
                conversation_id=conversation_id,
                message_id=message_id,
                trigger=signal.get("trigger"),
                event_type=f"user_{signal.get('user_emotion', 'NEUTRAL').lower()}",
                previous_state=previous_state.primary_emotion,
                new_state=saved_state.primary_emotion,
                intensity=intensity,
                confidence=signal.get("confidence", 1.0)
            )
            await self.emotion_repo.log_event(event)

        except Exception as e:
            logger.error(f"Failed to process emotion state: {e}")
