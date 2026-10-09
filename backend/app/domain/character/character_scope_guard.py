import logging
from app.domain.character.character_runtime_context import CharacterScope

logger = logging.getLogger(__name__)


class CharacterScopeViolationError(Exception):
    """Raised when an internal engine or provider attempts to process a mismatched character scope."""
    pass


class CharacterScopeGuard:
    """
    Runtime Guard against cross-character context leakage and scope contamination.
    Validates that providers, retrievers, and state machines are executing within the expected CharacterScope.
    """

    @staticmethod
    def assert_scope(
        expected_scope: CharacterScope,
        actual_companion_id: str,
        component_name: str = "CognitiveComponent",
        raise_error: bool = False
    ) -> bool:
        """
        Validates that actual_companion_id matches expected_scope.companion_id.
        In debug/test or strict mode, raises CharacterScopeViolationError.
        Otherwise logs a warning to prevent pipeline crash.
        """
        if expected_scope.companion_id != actual_companion_id:
            msg = (
                f"[ScopeViolation] {component_name} received mismatched companion_id '{actual_companion_id}', "
                f"expected '{expected_scope.companion_id}' for user '{expected_scope.user_id}'"
            )
            logger.warning(msg)
            if raise_error:
                raise CharacterScopeViolationError(msg)
            return False
        return True
