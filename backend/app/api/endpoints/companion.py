from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.services.companion.domain import NormalizedInput
from app.services.companion.orchestrator import CompanionOrchestrator
from app.services.companion.runtime import get_companion_orchestrator
import uuid

router = APIRouter(prefix="/companion", tags=["Companion Orchestrator"])

@router.post("/interactions")
async def process_interaction(
    input_data: NormalizedInput,
    orchestrator: CompanionOrchestrator = Depends(get_companion_orchestrator)
):
    """
    [OFFICIAL COGNITIVE RUNTIME ENTRYPOINT]
    Unified Endpoint for all Companion interactions (Text, Voice, Vision, Proactive).
    Routes input through CompanionOrchestrator -> 7 Context Providers -> LLM -> JSON SSE Stream.
    """
    try:
        if not input_data.interaction_id:
            input_data.interaction_id = f"INT-{uuid.uuid4().hex[:8]}"
            
        return StreamingResponse(
            orchestrator.process_interaction(input_data), 
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
