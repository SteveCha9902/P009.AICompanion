import logging
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.domain.character.character_runtime_context import CharacterScope

logger = logging.getLogger(__name__)


class AuthoritativeUserContext(BaseModel):
    """
    Verified, Authoritative User Identity derived from decoded JWT authentication tokens.
    Never relies solely on client-supplied body payloads.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: str = Field(..., description="Authoritative user ID")
    is_authenticated: bool = Field(default=True, description="Authentication flag")
    role: str = Field(default="user", description="User role ('user', 'admin')")
    tenant_id: Optional[str] = Field(default=None, description="Optional tenant or organization partition")


class MultiTenantScopeGuard:
    """
    Guards multi-user boundaries across all domain services.
    Enforces that User A can NEVER access or mutate User B's resources.
    """

    @staticmethod
    def assert_ownership(
        auth_context: AuthoritativeUserContext,
        target_user_id: str,
        resource_name: str = "resource"
    ) -> bool:
        """
        Asserts that the authenticated user strictly owns the requested resource.
        Raises PermissionError on mismatch (Fail Closed).
        """
        if not auth_context or not auth_context.is_authenticated:
            raise PermissionError("Unauthenticated request. Access denied.")

        if auth_context.user_id != target_user_id:
            logger.warning(
                f"[MultiTenantViolation] User '{auth_context.user_id}' attempted unauthorized access "
                f"to {resource_name} owned by '{target_user_id}'"
            )
            raise PermissionError(
                f"Access denied: You do not own this {resource_name}."
            )
        return True

    @staticmethod
    def create_character_scope(
        auth_context: AuthoritativeUserContext,
        companion_id: str
    ) -> CharacterScope:
        """
        Safely binds authoritative user_id with the target companion_id into a CharacterScope.
        """
        if not auth_context or not auth_context.is_authenticated:
            raise PermissionError("Unauthenticated user cannot create CharacterScope.")
        if not companion_id or companion_id.strip() == "":
            raise ValueError("companion_id cannot be empty.")

        return CharacterScope(
            user_id=auth_context.user_id,
            companion_id=companion_id
        )
