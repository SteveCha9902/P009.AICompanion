import logging
from typing import Optional, List
from app.domain.character.creation_request import CharacterCreationRequest
from app.services.character.template_registry import CharacterTemplateRegistry
from app.services.character.personality_compiler import MBTI_BASE_TRAITS

logger = logging.getLogger(__name__)


class CharacterValidationError(ValueError):
    """Validation failed on user input parameters."""
    pass


class CharacterDuplicateNameError(ValueError):
    """A character with the same normalized name already exists for this user."""
    pass


class CharacterCreationValidator:
    """
    Validates input parameters before initiating character creation transaction.
    """

    @classmethod
    def validate(
        cls,
        request: CharacterCreationRequest,
        existing_companion_names: Optional[List[str]] = None
    ):
        # 1. Name Validation
        if not request.name or not request.name.strip():
            raise CharacterValidationError("Character name cannot be empty.")
        
        trimmed_name = request.name.strip()
        if len(trimmed_name) > 50:
            raise CharacterValidationError("Character name cannot exceed 50 characters.")

        # 2. Duplicate Name Validation (within user scope)
        if existing_companion_names:
            normalized_req = trimmed_name.lower().replace(" ", "")
            for existing in existing_companion_names:
                if existing and existing.lower().replace(" ", "") == normalized_req:
                    raise CharacterDuplicateNameError(
                        f"A companion with name '{trimmed_name}' already exists for this user."
                    )

        # 3. MBTI Validation
        if request.mbti:
            mbti_upper = request.mbti.strip().upper()
            if mbti_upper not in MBTI_BASE_TRAITS:
                raise CharacterValidationError(
                    f"Invalid MBTI type '{request.mbti}'. Supported types: {', '.join(MBTI_BASE_TRAITS.keys())}"
                )

        # 4. Template Validation
        if request.template_id:
            available_templates = [t.template_id for t in CharacterTemplateRegistry.list_templates()]
            if request.template_id not in available_templates:
                logger.debug(f"Template '{request.template_id}' not found, falling back to 'custom'")
