import logging
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from app.domain.shared_experience.controlled_sharing import (
    ShareProposal,
    ShareProposalStatus,
    SharePolicy,
    ControlledSharedExperience,
    ShareCategory,
)
from app.services.shared_experience.policy_engine import SharingPolicyEngine

logger = logging.getLogger(__name__)


class ControlledSharingService:
    """
    Central service for managing Character-to-Character Controlled Shared Experiences.
    Handles proposal submission, user approval/denial, immediate revocation, and targeted retrieval.
    """

    def __init__(self, policy_engine: Optional[SharingPolicyEngine] = None):
        self.policy_engine = policy_engine or SharingPolicyEngine()
        self._proposals: Dict[str, ShareProposal] = {}
        self._experiences: Dict[str, ControlledSharedExperience] = {}
        self._cache: Dict[Tuple[str, str], List[ControlledSharedExperience]] = {}
        self._audit_logs: List[Dict] = []

    def propose_share(
        self,
        user_id: str,
        source_character_id: str,
        content: str,
        requested_targets: List[str],
        reason: str = "",
        category: ShareCategory = ShareCategory.FACT,
        source_interaction_id: Optional[str] = None,
        auto_approve_system_safe: bool = False
    ) -> ShareProposal:
        """
        Creates a new share proposal from a character.
        If system-safe, immediately converts into an active SharedExperience.
        """
        proposal = ShareProposal(
            source_character_id=source_character_id,
            user_id=user_id,
            content=content,
            requested_targets=requested_targets,
            reason=reason,
            category=category,
            source_interaction_id=source_interaction_id
        )

        status, policy, eval_reason = self.policy_engine.evaluate_proposal(
            proposal,
            user_explicit_approval=auto_approve_system_safe
        )
        proposal.status = status

        self._proposals[proposal.proposal_id] = proposal
        self._log_audit("SHARE_PROPOSED", user_id, source_character_id, proposal.proposal_id, {"status": status.value})

        if status == ShareProposalStatus.APPROVED:
            self._create_experience_from_proposal(proposal, policy)

        return proposal

    def approve_proposal(
        self,
        user_id: str,
        proposal_id: str,
        custom_targets: Optional[List[str]] = None
    ) -> ControlledSharedExperience:
        """
        User explicitly approves a pending share proposal.
        Converts proposal into an immutable ControlledSharedExperience.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal '{proposal_id}' not found.")
        if proposal.user_id != user_id:
            raise PermissionError("User does not own this proposal.")

        targets = custom_targets if custom_targets is not None else proposal.requested_targets
        proposal.status = ShareProposalStatus.APPROVED
        proposal.requested_targets = targets

        exp = self._create_experience_from_proposal(proposal, SharePolicy.USER_APPROVED)
        self._log_audit("SHARE_APPROVED", user_id, proposal.source_character_id, proposal_id, {"exp_id": exp.id})
        self.invalidate_cache(user_id)
        return exp

    def deny_proposal(self, user_id: str, proposal_id: str, reason: str = "") -> ShareProposal:
        """
        User explicitly denies a pending share proposal.
        """
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal '{proposal_id}' not found.")
        if proposal.user_id != user_id:
            raise PermissionError("User does not own this proposal.")

        proposal.status = ShareProposalStatus.DENIED
        self._log_audit("SHARE_DENIED", user_id, proposal.source_character_id, proposal_id, {"reason": reason})
        return proposal

    def revoke_experience(self, user_id: str, experience_id: str) -> bool:
        """
        Immediately revokes an active shared experience.
        Invalidates retrieval caches and prevents future access.
        """
        exp = self._experiences.get(experience_id)
        if not exp:
            return False
        if exp.user_id != user_id:
            raise PermissionError("User does not own this shared experience.")

        exp.is_revoked = True
        self._log_audit("SHARE_REVOKED", user_id, exp.source_character_id, experience_id, {})
        self.invalidate_cache(user_id)
        return True

    def get_shared_experiences(
        self,
        user_id: str,
        character_id: str,
        use_cache: bool = True
    ) -> List[ControlledSharedExperience]:
        """
        Retrieves all valid, non-revoked shared experiences accessible to the specified character.
        """
        cache_key = (user_id, character_id)
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        user_exps = [e for e in self._experiences.values() if e.user_id == user_id]
        accessible = self.policy_engine.filter_accessible_experiences(
            experiences=user_exps,
            user_id=user_id,
            character_id=character_id
        )

        self._cache[cache_key] = accessible
        self._log_audit("SHARE_RETRIEVED", user_id, character_id, None, {"count": len(accessible)})
        return accessible

    def invalidate_cache(self, user_id: str, character_id: Optional[str] = None):
        """
        Invalidates cached retrieval entries for the user.
        """
        if character_id:
            self._cache.pop((user_id, character_id), None)
        else:
            keys_to_remove = [k for k in self._cache.keys() if k[0] == user_id]
            for k in keys_to_remove:
                self._cache.pop(k, None)

    def _create_experience_from_proposal(
        self,
        proposal: ShareProposal,
        policy: SharePolicy
    ) -> ControlledSharedExperience:
        exp = ControlledSharedExperience(
            user_id=proposal.user_id,
            source_character_id=proposal.source_character_id,
            target_character_ids=proposal.requested_targets,
            content=proposal.content,
            category=proposal.category,
            policy=policy,
            source_interaction_id=proposal.source_interaction_id,
            source_proposal_id=proposal.proposal_id
        )
        self._experiences[exp.id] = exp
        return exp

    def _log_audit(self, action: str, user_id: str, character_id: Optional[str], ref_id: Optional[str], meta: Dict):
        self._audit_logs.append({
            "timestamp": datetime.utcnow(),
            "action": action,
            "user_id": user_id,
            "character_id": character_id,
            "ref_id": ref_id,
            "meta": meta
        })
