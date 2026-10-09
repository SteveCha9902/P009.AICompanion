import logging
from typing import List, Tuple, Optional
from datetime import datetime
from app.domain.shared_experience.controlled_sharing import (
    ShareProposal,
    SharePolicy,
    ShareProposalStatus,
    ControlledSharedExperience,
    ShareCategory,
)

logger = logging.getLogger(__name__)


class SharingPolicyEngine:
    """
    Evaluates sharing proposals against security boundaries, user permissions, and privacy rules.
    Enforces 'Private by Default' and 'Share Only by Policy'.
    """

    @staticmethod
    def evaluate_proposal(
        proposal: ShareProposal,
        user_explicit_approval: bool = False
    ) -> Tuple[ShareProposalStatus, SharePolicy, str]:
        """
        Evaluates whether a proposal should be Approved, Denied, or Kept Pending for User Approval.
        """
        if not proposal.user_id or not proposal.source_character_id:
            return ShareProposalStatus.DENIED, SharePolicy.PRIVATE, "Missing user_id or source_character_id"

        if not proposal.content or proposal.content.strip() == "":
            return ShareProposalStatus.DENIED, SharePolicy.PRIVATE, "Empty proposal content"

        # System Safe / Public Facts can be auto-approved
        if proposal.category == ShareCategory.SYSTEM_SAFE:
            return ShareProposalStatus.APPROVED, SharePolicy.SYSTEM_SAFE, "Auto-approved system safe category"

        # User Explicit Approval granted
        if user_explicit_approval or proposal.status == ShareProposalStatus.APPROVED:
            return ShareProposalStatus.APPROVED, SharePolicy.USER_APPROVED, "Explicit user approval granted"

        # Default requirement for user approval
        return ShareProposalStatus.PENDING, SharePolicy.USER_APPROVED, "Awaiting explicit user approval"

    @staticmethod
    def filter_accessible_experiences(
        experiences: List[ControlledSharedExperience],
        user_id: str,
        character_id: str
    ) -> List[ControlledSharedExperience]:
        """
        Filters a list of experiences ensuring strict User Isolation, Target Isolation, and Revocation checks.
        """
        accessible = []
        for exp in experiences:
            if exp.is_accessible_by(user_id=user_id, character_id=character_id):
                accessible.append(exp)
        return accessible
