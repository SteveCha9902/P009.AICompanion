from typing import Optional, List
from fastapi import APIRouter, Depends, Header, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.schemas.character_schema import (
    CharacterSummaryResponse,
    CharacterSummaryListResponse,
    ActivateCharacterResponse,
    CharacterCreateRequest,
    CharacterCreateResponse,
    CharacterUpdateRequest as CharacterUpdateRequestSchema,
    CharacterLifecycleResponse,
    CharacterVersionResponse,
    CharacterPresentationResponse,
    CharacterPresentationUpdateRequest,
)
from app.domain.character.creation_request import CharacterCreationRequest
from app.domain.character.update_request import CharacterUpdateRequest
from app.repositories.character_registry_repository import CharacterRegistryRepository
from app.services.character.registry_service import CharacterRegistryService
from app.services.character.creation_service import CharacterCreationService
from app.services.character.lifecycle_service import CharacterLifecycleService
from app.services.character.context_resolver import CharacterContextResolver
from app.services.character.presentation_resolver import CharacterPresentationResolver
from app.services.character.creation_validator import (
    CharacterValidationError,
    CharacterDuplicateNameError
)

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/characters", tags=["Characters"])


def get_character_registry_service(db: AsyncSession = Depends(get_db)) -> CharacterRegistryService:
    repo = CharacterRegistryRepository(db)
    return CharacterRegistryService(repository=repo, db_session=db)


def get_character_creation_service(db: AsyncSession = Depends(get_db)) -> CharacterCreationService:
    repo = CharacterRegistryRepository(db)
    return CharacterCreationService(db_session=db, registry_repo=repo)


def get_character_presentation_resolver(db: AsyncSession = Depends(get_db)) -> CharacterPresentationResolver:
    repo = CharacterRegistryRepository(db)
    return CharacterPresentationResolver(db=db, registry_repo=repo)


def get_character_lifecycle_service(db: AsyncSession = Depends(get_db)) -> CharacterLifecycleService:
    repo = CharacterRegistryRepository(db)
    reg_service = CharacterRegistryService(repository=repo, db_session=db)
    pres_resolver = CharacterPresentationResolver(db=db, registry_repo=repo)
    resolver = CharacterContextResolver(db=db, registry_service=reg_service, presentation_resolver=pres_resolver)
    return CharacterLifecycleService(
        db_session=db,
        registry_repo=repo,
        registry_service=reg_service,
        context_resolver=resolver
    )


@router.get("", response_model=CharacterSummaryListResponse)
async def list_characters(
    include_archived: bool = Query(default=False, description="Include archived companions in listing"),
    x_user_id: Optional[str] = Header(default="default_user"),
    service: CharacterRegistryService = Depends(get_character_registry_service)
):
    """
    Lists all characters owned by the authenticated user with active state indicators.
    """
    summaries = await service.list_characters(user_id=x_user_id, include_archived=include_archived)
    items = [
        CharacterSummaryResponse(
            companion_id=s.companion_id,
            name=s.name,
            role_title=s.role_title,
            avatar_preview=s.avatar_preview,
            voice_name=s.voice_name,
            is_active=s.is_active
        )
        for s in summaries
    ]
    return CharacterSummaryListResponse(characters=items, total_count=len(items))


@router.get("/active", response_model=CharacterSummaryResponse)
async def get_active_character(
    x_user_id: Optional[str] = Header(default="default_user"),
    service: CharacterRegistryService = Depends(get_character_registry_service)
):
    """
    Retrieves the currently active character for the authenticated user.
    """
    summaries = await service.list_characters(user_id=x_user_id)
    for s in summaries:
        if s.is_active:
            return CharacterSummaryResponse(
                companion_id=s.companion_id,
                name=s.name,
                role_title=s.role_title,
                avatar_preview=s.avatar_preview,
                voice_name=s.voice_name,
                is_active=True
            )
    
    # Fallback to first if none marked active
    if summaries:
        s0 = summaries[0]
        return CharacterSummaryResponse(
            companion_id=s0.companion_id,
            name=s0.name,
            role_title=s0.role_title,
            avatar_preview=s0.avatar_preview,
            voice_name=s0.voice_name,
            is_active=True
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No active companion found for user {x_user_id}"
    )


@router.post("/{companion_id}/activate", response_model=ActivateCharacterResponse)
async def activate_character(
    companion_id: str,
    x_user_id: Optional[str] = Header(default="default_user"),
    service: CharacterRegistryService = Depends(get_character_registry_service)
):
    """
    Atomically switches the user's active character to the specified companion_id.
    Enforces ownership validation and prevents cross-user activation.
    """
    try:
        active_summary = await service.set_active_companion(user_id=x_user_id, companion_id=companion_id)
        return ActivateCharacterResponse(
            active_companion_id=active_summary.companion_id,
            character=CharacterSummaryResponse(
                companion_id=active_summary.companion_id,
                name=active_summary.name,
                role_title=active_summary.role_title,
                avatar_preview=active_summary.avatar_preview,
                voice_name=active_summary.voice_name,
                is_active=True
            ),
            message=f"Successfully switched active companion to {active_summary.name}"
        )
    except PermissionError as pe:
        logger.warning(f"[API] Ownership validation rejected: {pe}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(pe)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"[API] Unexpected error during companion activation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch active character"
        )


from app.api.schemas.character_schema import (
    CharacterSummaryResponse,
    CharacterSummaryListResponse,
    ActivateCharacterResponse,
    CharacterCreateRequest,
    CharacterCreateResponse,
    CharacterPreviewRequest,
    CharacterPreviewResponse,
    CharacterUpdateRequest as CharacterUpdateRequestSchema,
    CharacterLifecycleResponse,
    CharacterVersionResponse,
    CharacterPresentationResponse,
    CharacterPresentationUpdateRequest,
)


@router.post("/preview", response_model=CharacterPreviewResponse)
async def preview_character(
    payload: CharacterPreviewRequest,
    x_user_id: Optional[str] = Header(default="default_user"),
    creation_service: CharacterCreationService = Depends(get_character_creation_service)
):
    """
    Compiles and previews character DNA without saving to database.
    """
    try:
        domain_req = CharacterCreationRequest(
            user_id=x_user_id,
            name=payload.name,
            template_id=payload.template_id or "custom",
            role_title=payload.role_title,
            tagline=payload.tagline,
            relationship_type=payload.relationship_type,
            mbti=payload.mbti,
            personality_keywords=payload.personality_keywords,
            interests=payload.interests,
            speaking_style=payload.speaking_style,
            speech_profile=payload.speech_profile or {},
            voice_id=payload.voice_id,
            avatar_preset=payload.avatar_preset,
            behavior_rules=payload.behavior_rules,
            origin_story=payload.origin_story
        )
        preview_data = await creation_service.preview_character(domain_req)
        return CharacterPreviewResponse(**preview_data)
    except Exception as e:
        logger.error(f"[API] Error compiling character preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview compilation failed: {str(e)}"
        )


@router.post("", response_model=CharacterCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    payload: CharacterCreateRequest,
    x_user_id: Optional[str] = Header(default="default_user"),
    creation_service: CharacterCreationService = Depends(get_character_creation_service)
):
    """
    Atomically provisions a new companion character with compiled DNA and initial runtime state.
    Created characters are inactive by default.
    """
    try:
        domain_req = CharacterCreationRequest(
            user_id=x_user_id,
            name=payload.name,
            template_id=payload.template_id or "custom",
            role_title=payload.role_title,
            tagline=payload.tagline,
            relationship_type=payload.relationship_type,
            mbti=payload.mbti,
            personality_keywords=payload.personality_keywords,
            interests=payload.interests,
            speaking_style=payload.speaking_style,
            speech_profile=payload.speech_profile or {},
            voice_id=payload.voice_id,
            avatar_preset=payload.avatar_preset,
            behavior_rules=payload.behavior_rules,
            origin_story=payload.origin_story
        )
        result = await creation_service.create_character(domain_req)
        return CharacterCreateResponse(
            companion_id=result.companion_id,
            name=result.name,
            role_title=result.role_title,
            status=result.status,
            is_active=result.is_active,
            message=result.message
        )
    except CharacterDuplicateNameError as dne:
        logger.warning(f"[API] Character duplicate name conflict: {dne}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(dne)
        )
    except CharacterValidationError as ve:
        logger.warning(f"[API] Character validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"[API] Unexpected error during character creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Character creation failed: {str(e)}"
        )


@router.patch("/{companion_id}", response_model=CharacterLifecycleResponse)
async def update_character(
    companion_id: str,
    payload: CharacterUpdateRequestSchema,
    x_user_id: Optional[str] = Header(default="default_user"),
    service: CharacterLifecycleService = Depends(get_character_lifecycle_service)
):
    """
    Updates character configuration, compiles personality DNA changes, and generates version snapshots.
    """
    try:
        domain_req = CharacterUpdateRequest(
            user_id=x_user_id,
            companion_id=companion_id,
            role_title=payload.role_title,
            mbti=payload.mbti,
            personality_keywords=payload.personality_keywords,
            speaking_style=payload.speaking_style,
            voice_id=payload.voice_id,
            avatar_preset=payload.avatar_preset,
            origin_story=payload.origin_story
        )
        updated_summary = await service.update_character(x_user_id, companion_id, domain_req)
        return CharacterLifecycleResponse(
            companion_id=updated_summary.companion_id,
            name=updated_summary.name,
            status="updated",
            character=CharacterSummaryResponse(
                companion_id=updated_summary.companion_id,
                name=updated_summary.name,
                role_title=updated_summary.role_title,
                avatar_preview=updated_summary.avatar_preview,
                voice_name=updated_summary.voice_name,
                is_active=updated_summary.is_active
            ),
            message=f"Character '{updated_summary.name}' evolved successfully"
        )
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        logger.error(f"[API] Error updating character: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{companion_id}/archive", response_model=CharacterLifecycleResponse)
async def archive_character(
    companion_id: str,
    x_user_id: Optional[str] = Header(default="default_user"),
    service: CharacterLifecycleService = Depends(get_character_lifecycle_service)
):
    """
    Archives an inactive companion character.
    Rejects active or system default character archival with 409 Conflict / 403 Forbidden.
    """
    try:
        summary = await service.archive_character(x_user_id, companion_id)
        return CharacterLifecycleResponse(
            companion_id=summary.companion_id,
            name=summary.name,
            status="archived",
            character=CharacterSummaryResponse(
                companion_id=summary.companion_id,
                name=summary.name,
                role_title=summary.role_title,
                avatar_preview=summary.avatar_preview,
                voice_name=summary.voice_name,
                is_active=False
            ),
            message=f"Character '{summary.name}' archived successfully"
        )
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{companion_id}/restore", response_model=CharacterLifecycleResponse)
async def restore_character(
    companion_id: str,
    x_user_id: Optional[str] = Header(default="default_user"),
    service: CharacterLifecycleService = Depends(get_character_lifecycle_service)
):
    """
    Restores an archived companion character back to available status.
    Rejects restoring deleted characters with 409 Conflict.
    """
    try:
        summary = await service.restore_character(x_user_id, companion_id)
        return CharacterLifecycleResponse(
            companion_id=summary.companion_id,
            name=summary.name,
            status="restored",
            character=CharacterSummaryResponse(
                companion_id=summary.companion_id,
                name=summary.name,
                role_title=summary.role_title,
                avatar_preview=summary.avatar_preview,
                voice_name=summary.voice_name,
                is_active=summary.is_active
            ),
            message=f"Character '{summary.name}' restored successfully"
        )
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{companion_id}", response_model=CharacterLifecycleResponse)
async def delete_character(
    companion_id: str,
    x_user_id: Optional[str] = Header(default="default_user"),
    service: CharacterLifecycleService = Depends(get_character_lifecycle_service)
):
    """
    Soft deletes a companion character.
    Rejects active or system default character deletion with 409 Conflict / 403 Forbidden.
    """
    try:
        summary = await service.delete_character(x_user_id, companion_id)
        return CharacterLifecycleResponse(
            companion_id=summary.companion_id,
            name=summary.name,
            status="deleted",
            character=CharacterSummaryResponse(
                companion_id=summary.companion_id,
                name=summary.name,
                role_title=summary.role_title,
                avatar_preview=summary.avatar_preview,
                voice_name=summary.voice_name,
                is_active=False
            ),
            message=f"Character '{summary.name}' soft deleted successfully"
        )
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{companion_id}/versions", response_model=List[CharacterVersionResponse])
async def get_character_versions(
    companion_id: str,
    x_user_id: Optional[str] = Header(default="default_user"),
    service: CharacterLifecycleService = Depends(get_character_lifecycle_service)
):
    """
    Retrieves the DNA evolution version audit history for a companion character.
    """
    try:
        history = await service.get_version_history(x_user_id, companion_id)
        return [
            CharacterVersionResponse(
                version=h["version"],
                change_type=h["change_type"],
                dna_snapshot=h["dna_snapshot"],
                created_at=h["created_at"]
            )
            for h in history
        ]
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{companion_id}/presentation", response_model=CharacterPresentationResponse)
async def get_character_presentation(
    companion_id: str,
    x_user_id: Optional[str] = Header(default="default_user"),
    resolver: CharacterPresentationResolver = Depends(get_character_presentation_resolver)
):
    """
    Retrieves the character-specific presentation profile (Voice + Avatar + Expression + Gesture).
    """
    try:
        ctx = await resolver.resolve(user_id=x_user_id, companion_id=companion_id)
        return CharacterPresentationResponse(
            companion_id=ctx.companion_id,
            voice={
                "provider": ctx.voice.provider,
                "voice_id": ctx.voice.voice_id,
                "persona_type": ctx.voice.persona_type,
                "speaking_rate": ctx.voice.speaking_rate,
                "pitch_offset": ctx.voice.pitch_offset,
                "warmth": ctx.voice.warmth,
                "energy": ctx.voice.energy,
                "empathy": ctx.voice.empathy,
            },
            avatar={
                "avatar_id": ctx.avatar.avatar_id,
                "visual_style": ctx.avatar.visual_style,
                "default_expression": ctx.avatar.default_expression,
                "default_motion": ctx.avatar.default_motion,
            },
            expression={
                "style": ctx.expression.style,
                "gaze_style": ctx.expression.gaze_style,
                "available_expressions": ctx.expression.available_expressions,
            },
            gesture={
                "style": ctx.gesture.style,
                "frequency": ctx.gesture.frequency,
                "available_gestures": ctx.gesture.available_gestures,
            }
        )
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except Exception as e:
        logger.error(f"[API] Error resolving character presentation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{companion_id}/presentation", response_model=CharacterPresentationResponse)
async def update_character_presentation(
    companion_id: str,
    payload: CharacterPresentationUpdateRequest,
    x_user_id: Optional[str] = Header(default="default_user"),
    resolver: CharacterPresentationResolver = Depends(get_character_presentation_resolver)
):
    """
    Updates the character-specific presentation profile (Voice, Avatar, Expression, Gesture)
    and invalidates the runtime presentation cache.
    """
    try:
        ctx = await resolver.update_presentation(
            user_id=x_user_id,
            companion_id=companion_id,
            voice_updates=payload.voice,
            avatar_updates=payload.avatar,
            expression_updates=payload.expression,
            gesture_updates=payload.gesture
        )
        return CharacterPresentationResponse(
            companion_id=ctx.companion_id,
            voice={
                "provider": ctx.voice.provider,
                "voice_id": ctx.voice.voice_id,
                "persona_type": ctx.voice.persona_type,
                "speaking_rate": ctx.voice.speaking_rate,
                "pitch_offset": ctx.voice.pitch_offset,
                "warmth": ctx.voice.warmth,
                "energy": ctx.voice.energy,
                "empathy": ctx.voice.empathy,
            },
            avatar={
                "avatar_id": ctx.avatar.avatar_id,
                "visual_style": ctx.avatar.visual_style,
                "default_expression": ctx.avatar.default_expression,
                "default_motion": ctx.avatar.default_motion,
            },
            expression={
                "style": ctx.expression.style,
                "gaze_style": ctx.expression.gaze_style,
                "available_expressions": ctx.expression.available_expressions,
            },
            gesture={
                "style": ctx.gesture.style,
                "frequency": ctx.gesture.frequency,
                "available_gestures": ctx.gesture.available_gestures,
            }
        )
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except Exception as e:
        logger.error(f"[API] Error updating character presentation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
