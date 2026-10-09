import logging
import asyncio
import time
from typing import AsyncGenerator, Optional, Set
from app.services.companion.domain import (
    NormalizedInput, 
    StructuredCandidate, 
    UnifiedResponse, 
    SSEEventType, 
    format_sse_event,
    EmotionCandidate,
    RelationshipSignal,
    PresentationHint
)
from app.services.companion.events.bus import CompanionEventBus
from app.services.companion.events.events import CompanionEvent, EventType, EventPriority
from app.services.companion.state.interaction_state import InteractionStateMachine, CompanionInteractionState
from app.services.context.builder import ContextBuilder
from app.services.llm.base import BaseLLMProvider, LLMProviderError
from app.services.presentation_engine import AvatarStateResolver
from app.repositories.message_repository import MessageRepository
from app.services.companion.observability.tracer import InteractionTracer
from app.services.character.context_resolver import CharacterContextResolver
from app.domain.character.character_runtime_context import CharacterRuntimeContext
from app.domain.character.character_scope_guard import CharacterScopeGuard
from app.domain.interaction.interaction_context import InteractionContext
import json
import uuid

logger = logging.getLogger(__name__)

# Global Active Interaction Registry for Idempotency Guard
active_interactions: Set[str] = set()

# Hierarchical Timeout Constants
TTFT_TIMEOUT_SECONDS = 15.0       # Max wait for first token
STREAM_IDLE_TIMEOUT_SECONDS = 30.0 # Max gap between streaming chunks

class CompanionOrchestrator:
    """
    Hardened Unified Orchestrator for all Companion interactions.
    Coordinates: Idempotency Check -> Input Normalization -> Character Runtime Resolution ->
                 Context Assembly -> Timed LLM Stream -> Candidate Validation -> 
                 Avatar Resolution -> Message Persistence -> Clean User SSE -> Structured Observability Log
    """
    def __init__(self, 
                 event_bus: CompanionEventBus, 
                 state_machine: InteractionStateMachine,
                 context_builder: ContextBuilder,
                 llm_provider: BaseLLMProvider,
                 avatar_resolver: Optional[AvatarStateResolver] = None,
                 message_repo: Optional[MessageRepository] = None,
                 context_resolver: Optional[CharacterContextResolver] = None):
        self.event_bus = event_bus
        self.state_machine = state_machine
        self.context_builder = context_builder
        self.llm_provider = llm_provider
        self.avatar_resolver = avatar_resolver
        self.message_repo = message_repo
        self.context_resolver = context_resolver or CharacterContextResolver()

    async def process_interaction(self, user_input: NormalizedInput) -> AsyncGenerator[str, None]:
        """
        Main Hardened Pipeline yielding JSON SSE Events with sequence IDs:
        interaction_started -> thinking -> text_delta -> text_completed -> avatar_state -> interaction_completed
        """
        interaction_id = user_input.interaction_id or str(uuid.uuid4())
        seq = 0

        # 0. Idempotency Guard
        if interaction_id in active_interactions:
            logger.warning(f"[IdempotencyGuard] Duplicate request ignored for active interaction_id: {interaction_id}")
            seq += 1
            yield format_sse_event(
                SSEEventType.ERROR, 
                {"message": "Duplicate interaction in progress", "interaction_id": interaction_id},
                event_id=f"{interaction_id}:{seq}"
            )
            return

        active_interactions.add(interaction_id)
        tracer: Optional[InteractionTracer] = None
        
        try:
            # SB-1 & SB-3: Resolve Immutable CharacterRuntimeContext and create InteractionContext Snapshot
            runtime_ctx = await self.context_resolver.resolve(
                user_id=user_input.user_id,
                companion_id=user_input.companion_id
            )
            canonical_companion_id = runtime_ctx.scope.companion_id
            
            interaction_ctx = InteractionContext(
                interaction_id=interaction_id,
                character_scope=runtime_ctx.scope,
                character_runtime_context=runtime_ctx
            )
            CharacterScopeGuard.assert_scope(
                expected_scope=interaction_ctx.character_scope,
                actual_companion_id=canonical_companion_id,
                component_name="CompanionOrchestrator"
            )

            tracer = InteractionTracer(
                interaction_id=interaction_id,
                user_id=user_input.user_id,
                companion_id=canonical_companion_id,
                modality=user_input.input_type.value
            )
            tracer.mark_input_norm_start()

            # 1. State: LISTENING -> ANALYZING
            self.state_machine.transition_to(CompanionInteractionState.ANALYZING, interaction_id)
            tracer.mark_input_norm_end()
            
            seq += 1
            yield format_sse_event(
                SSEEventType.INTERACTION_STARTED, 
                {
                    "interaction_id": interaction_id,
                    "companion_id": canonical_companion_id,
                    "user_id": user_input.user_id,
                    "modality": user_input.input_type.value
                },
                event_id=f"{interaction_id}:{seq}"
            )
            
            payload_data = user_input.model_dump() if hasattr(user_input, "model_dump") else user_input.dict()
            await self.event_bus.publish(CompanionEvent(
                event_id=str(uuid.uuid4()),
                interaction_id=interaction_id,
                event_type=EventType.USER_INPUT_RECEIVED,
                priority=EventPriority.SYNC,
                payload={"input": payload_data}
            ))

            # 2. State: THINKING & Context Assembly
            self.state_machine.transition_to(CompanionInteractionState.THINKING, interaction_id)
            seq += 1
            yield format_sse_event(
                SSEEventType.THINKING, 
                {"status": "assembling_context"},
                event_id=f"{interaction_id}:{seq}"
            )

            tracer.mark_context_start()
            # 2.5 Resolve Character Decision (Sprint 36)
            char_decision = None
            try:
                from app.services.character.behavior_engine import CharacterBehaviorEngine
                from app.domain.relationship.relationship_stage import RelationshipStage
                char_decision = CharacterBehaviorEngine.resolve_decision(
                    user_input=user_input.content,
                    relationship_stage=RelationshipStage.FRIEND
                )
            except Exception as dec_err:
                logger.warning(f"[Orchestrator] CharacterDecision resolution fallback: {dec_err}")

            try:
                context = await self.context_builder.build(
                    conversation_id=user_input.conversation_id,
                    current_user_message=user_input.content,
                    companion_id=canonical_companion_id,
                    runtime_ctx=runtime_ctx
                )
                if char_decision and char_decision.prompt_directive:
                    context.insert(1, {"role": "system", "content": char_decision.prompt_directive})
            except Exception as e:
                logger.error(f"Context Assembly failed: {e}")
                context = [
                    {"role": "system", "content": "You are an AI companion."},
                    {"role": "user", "content": user_input.content}
                ]
            tracer.mark_context_end()
            
            await self.event_bus.publish(CompanionEvent(
                event_id=str(uuid.uuid4()),
                interaction_id=interaction_id,
                event_type=EventType.CONTEXT_ASSEMBLED,
                priority=EventPriority.SYNC,
                payload={"context_length": len(context)}
            ))


            # 3. LLM Streaming with Hierarchical Timeouts
            self.state_machine.transition_to(CompanionInteractionState.RESPONDING, interaction_id)
            tracer.mark_llm_start()
            
            full_text = ""
            stream_iter = self.llm_provider.stream(context).__aiter__()
            
            # TTFT (Time To First Token) Guard
            try:
                first_chunk = await asyncio.wait_for(stream_iter.__anext__(), timeout=TTFT_TIMEOUT_SECONDS)
                first_chunk_text = first_chunk.content if hasattr(first_chunk, "content") else str(first_chunk)
                full_text += first_chunk_text
                tracer.mark_first_token()
                
                seq += 1
                yield format_sse_event(
                    SSEEventType.TEXT_DELTA, 
                    {"delta": first_chunk_text},
                    event_id=f"{interaction_id}:{seq}"
                )
            except StopAsyncIteration:
                pass
            except asyncio.TimeoutError:
                raise TimeoutError(f"TTFT Timeout ({TTFT_TIMEOUT_SECONDS}s) exceeded while waiting for first token.")

            # Remaining stream with Stream Idle Timeout
            while True:
                try:
                    chunk = await asyncio.wait_for(stream_iter.__anext__(), timeout=STREAM_IDLE_TIMEOUT_SECONDS)
                    chunk_text = chunk.content if hasattr(chunk, "content") else str(chunk)
                    full_text += chunk_text
                    tracer.mark_token()
                    
                    seq += 1
                    yield format_sse_event(
                        SSEEventType.TEXT_DELTA, 
                        {"delta": chunk_text},
                        event_id=f"{interaction_id}:{seq}"
                    )
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Stream Idle Timeout ({STREAM_IDLE_TIMEOUT_SECONDS}s) exceeded.")

            tracer.mark_llm_end()

            # 4. Text Completed
            seq += 1
            yield format_sse_event(
                SSEEventType.TEXT_COMPLETED, 
                {"full_text": full_text},
                event_id=f"{interaction_id}:{seq}"
            )

            # 5. Post Processing & Candidate Parsing
            tracer.mark_post_process_start()
            candidate = None
            try:
                if full_text.strip().startswith("{") and full_text.strip().endswith("}"):
                    candidate_dict = json.loads(full_text)
                    candidate = StructuredCandidate(**candidate_dict)
                    response_clean_text = candidate.response_text
                else:
                    candidate = StructuredCandidate(response_text=full_text)
                    response_clean_text = full_text
            except Exception as e:
                logger.warning(f"Structured Candidate parsing fallback to raw text: {e}")
                candidate = StructuredCandidate(response_text=full_text)
                response_clean_text = full_text

            cand_payload = candidate.model_dump() if hasattr(candidate, "model_dump") else candidate.dict()
            
            # 5.5 Multidimensional Character Consistency Validation & Guard (Sprint 36 & 37)
            try:
                from app.services.character.consistency import CharacterConsistencyValidator
                from app.services.character.relationship.evolution import RelationshipEvolutionEngine
                from app.domain.relationship.relationship_stage import RelationshipStage

                if char_decision is not None:
                    val_res = CharacterConsistencyValidator.validate(
                        response_text=response_clean_text,
                        decision=char_decision,
                        relationship_stage=RelationshipStage.FRIEND
                    )
                    cand_payload["consistency_score"] = val_res.overall_score
                    cand_payload["consistency_verdict"] = val_res.status
                    cand_payload["validation_details"] = val_res.model_dump()
                    if val_res.violations:
                        logger.info(f"[Orchestrator] Consistency violations: {val_res.violations}")

                # Calculate Sprint 37 Bounded Relationship Delta
                rel_delta = RelationshipEvolutionEngine.calculate_delta(
                    user_input=user_input.content,
                    significance=0.6
                )
                cand_payload["relationship_delta"] = rel_delta.model_dump()
            except Exception as val_err:
                logger.warning(f"[Orchestrator] Character validation / evolution error: {val_err}")

            await self.event_bus.publish(CompanionEvent(
                event_id=str(uuid.uuid4()),
                interaction_id=interaction_id,
                event_type=EventType.LLM_CANDIDATE_GENERATED,
                priority=EventPriority.ASYNC,
                payload={"candidate": cand_payload}
            ))


            # 6. AvatarStateResolver & PresentationIntent Integration (Sprint 36)
            resolved_avatar_state = {}
            if self.avatar_resolver:
                try:
                    resolved_avatar_state = self.avatar_resolver.resolve(canonical_companion_id)
                except Exception as e:
                    logger.warning(f"AvatarStateResolver failed: {e}")
                    resolved_avatar_state = {"expression": "neutral", "animation": "idle", "intensity": 0.5}

            if char_decision is not None:
                try:
                    from app.services.character.presentation_mapper import PresentationIntentMapper
                    from app.services.character.avatar.behavior_controller import AvatarBehaviorController
                    from app.services.character.avatar.domain import AvatarBehavioralState

                    p_intent = PresentationIntentMapper.map_decision_to_presentation(char_decision)
                    avatar_plan = AvatarBehaviorController.evaluate_plan(
                        state=AvatarBehavioralState.SPEAKING,
                        decision=char_decision
                    )

                    resolved_avatar_state.update({
                        "expression": p_intent.facial_expression,
                        "animation": p_intent.gesture_type,
                        "energy": p_intent.animation_energy,
                        "gaze": p_intent.gaze_behavior,
                        "intensity": p_intent.gesture_intensity,
                        "expression_parameters": avatar_plan.expression.model_dump(),
                        "active_gestures": [g.model_dump() for g in avatar_plan.active_gestures],
                        "behavioral_state": avatar_plan.state.value,
                        "attention_level": avatar_plan.attention_level
                    })
                except Exception as p_err:
                    logger.warning(f"[Orchestrator] Presentation / Avatar mapping fallback: {p_err}")

            
            if candidate and candidate.presentation:
                resolved_avatar_state.update({
                    "expression": candidate.presentation.expression,
                    "energy": candidate.presentation.energy,
                    "animation": candidate.presentation.animation,
                    "gaze": candidate.presentation.gaze
                })


            seq += 1
            yield format_sse_event(
                SSEEventType.AVATAR_STATE, 
                {"avatar_state": resolved_avatar_state},
                event_id=f"{interaction_id}:{seq}"
            )

            # 6.5 Persist Messages for Conversation Continuity
            if self.message_repo and user_input.conversation_id and user_input.conversation_id != "default":
                try:
                    await self.message_repo.create(
                        conversation_id=user_input.conversation_id,
                        role="user",
                        content=user_input.content
                    )
                    await self.message_repo.create(
                        conversation_id=user_input.conversation_id,
                        role="assistant",
                        content=response_clean_text
                    )
                except Exception as e:
                    logger.warning(f"Failed to persist messages: {e}")

            tracer.mark_post_process_end()

            # 7. Interaction Completed (Clean User Protocol)
            self.state_machine.transition_to(CompanionInteractionState.IDLE, interaction_id)
            seq += 1
            yield format_sse_event(
                SSEEventType.INTERACTION_COMPLETED, 
                {
                    "interaction_id": interaction_id,
                    "text": response_clean_text,
                    "avatar_state": resolved_avatar_state
                },
                event_id=f"{interaction_id}:{seq}"
            )

            tracer.mark_completed()

        except asyncio.CancelledError:
            logger.info(f"[Orchestrator] Interaction {interaction_id} CANCELLED by client disconnect.")
            self.state_machine.transition_to(CompanionInteractionState.IDLE, interaction_id)
            if tracer:
                tracer.mark_error("Client disconnected / cancelled")
            raise

        except LLMProviderError as e:
            self.state_machine.transition_to(CompanionInteractionState.ERROR, interaction_id)
            logger.error(f"[Orchestrator] LLM Provider error ({e.code}): {e.message}")
            if tracer:
                tracer.mark_error(f"{e.code}: {e.message}")
            seq += 1
            yield format_sse_event(
                SSEEventType.ERROR, 
                {"error_code": e.code, "message": "잠시 문제가 생겼어요. 다시 시도해 주세요."},
                event_id=f"{interaction_id}:{seq}"
            )

        except Exception as e:
            self.state_machine.transition_to(CompanionInteractionState.ERROR, interaction_id)
            logger.error(f"Interaction {interaction_id} failed: {e}")
            if tracer:
                tracer.mark_error(str(e))
            seq += 1
            yield format_sse_event(
                SSEEventType.ERROR, 
                {"error_code": "INTERNAL_ERROR", "message": "대화 처리 중 오류가 발생했습니다."},
                event_id=f"{interaction_id}:{seq}"
            )

        finally:
            active_interactions.discard(interaction_id)

    async def process_interaction_sync(self, user_input: NormalizedInput) -> UnifiedResponse:
        """
        Synchronous helper for VoiceService or non-streaming callers.
        """
        interaction_id = user_input.interaction_id or str(uuid.uuid4())
        
        runtime_ctx = await self.context_resolver.resolve(
            user_id=user_input.user_id,
            companion_id=user_input.companion_id
        )
        canonical_companion_id = runtime_ctx.scope.companion_id
        
        interaction_ctx = InteractionContext(
            interaction_id=interaction_id,
            character_scope=runtime_ctx.scope,
            character_runtime_context=runtime_ctx
        )
        CharacterScopeGuard.assert_scope(
            expected_scope=interaction_ctx.character_scope,
            actual_companion_id=canonical_companion_id,
            component_name="CompanionOrchestratorSync"
        )

        try:
            context = await self.context_builder.build(
                conversation_id=user_input.conversation_id,
                current_user_message=user_input.content,
                companion_id=canonical_companion_id,
                runtime_ctx=runtime_ctx
            )
        except Exception:
            context = [
                {"role": "system", "content": "You are an AI companion."},
                {"role": "user", "content": user_input.content}
            ]

        full_text = ""
        async for chunk in self.llm_provider.stream(context):
            chunk_text = chunk.content if hasattr(chunk, "content") else str(chunk)
            full_text += chunk_text

        avatar_state = {}
        if self.avatar_resolver:
            try:
                avatar_state = self.avatar_resolver.resolve(canonical_companion_id)
            except Exception:
                avatar_state = {"expression": "neutral", "animation": "idle"}

        return UnifiedResponse(
            interaction_id=interaction_id,
            text=full_text,
            avatar_state=avatar_state,
            metadata=user_input.metadata
        )

    async def process_interaction_stream_chunks(self, user_input: NormalizedInput):
        """
        Asynchronously streams semantic text chunks (sentences/clauses) as LLM generates tokens.
        Yields (chunk_text: str, is_last: bool, avatar_state: dict).
        """
        from app.services.voice.chunk_manager import SemanticChunkManager
        chunk_mgr = SemanticChunkManager()

        interaction_id = user_input.interaction_id or str(uuid.uuid4())
        runtime_ctx = await self.context_resolver.resolve(
            user_id=user_input.user_id,
            companion_id=user_input.companion_id
        )
        canonical_companion_id = runtime_ctx.scope.companion_id

        try:
            context = await self.context_builder.build(
                conversation_id=user_input.conversation_id,
                current_user_message=user_input.content,
                companion_id=canonical_companion_id,
                runtime_ctx=runtime_ctx
            )
        except Exception:
            context = [
                {"role": "system", "content": "You are an AI companion."},
                {"role": "user", "content": user_input.content}
            ]

        avatar_state = {}
        if self.avatar_resolver:
            try:
                avatar_state = self.avatar_resolver.resolve(canonical_companion_id)
            except Exception:
                avatar_state = {"expression": "speaking", "animation": "nod"}

        full_text = ""
        async for chunk in self.llm_provider.stream(context):
            chunk_text = chunk.content if hasattr(chunk, "content") else str(chunk)
            full_text += chunk_text
            ready_chunks = chunk_mgr.push(chunk_text)
            for c in ready_chunks:
                yield c, False, avatar_state, full_text

        # Flush final remainder
        remaining_chunks = chunk_mgr.flush()
        for c in remaining_chunks:
            yield c, True, avatar_state, full_text

