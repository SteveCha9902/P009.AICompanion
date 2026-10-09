from typing import Optional, Dict, List
import time
from app.domain.goal.goal import Goal, GoalCandidate, GoalType, GoalStatus, GoalMilestone

class PlanningEngine:
    """
    Manages structured Goal creation upon user approval, milestone decomposition, and gentle archiving.
    """

    _goals: Dict[str, List[Goal]] = {}

    @classmethod
    def confirm_and_create_goal(
        cls,
        candidate: GoalCandidate,
        initial_milestones: Optional[List[str]] = None,
        target_date_str: str = "",
        commitment_level: float = 0.60
    ) -> Goal:
        user_id = candidate.user_id
        if user_id not in cls._goals:
            cls._goals[user_id] = []

        m_objs = []
        if initial_milestones:
            for i, m_title in enumerate(initial_milestones):
                m_objs.append(GoalMilestone(
                    milestone_id=f"ms_{int(time.time()*1000)}_{i}",
                    title=m_title
                ))

        goal = Goal(
            goal_id=f"goal_{int(time.time()*1000)}",
            user_id=user_id,
            title=candidate.title,
            goal_type=candidate.goal_type,
            status=GoalStatus.ACTIVE,
            confidence=candidate.confidence,
            commitment_level=commitment_level,
            milestones=m_objs,
            target_date_str=target_date_str
        )
        cls._goals[user_id].append(goal)
        return goal

    @classmethod
    def list_user_goals(cls, user_id: str, include_archived: bool = False) -> List[Goal]:
        if user_id not in cls._goals:
            return []
        if include_archived:
            return list(cls._goals[user_id])
        return [g for g in cls._goals[user_id] if g.status != GoalStatus.ARCHIVED]

    @classmethod
    def complete_milestone(cls, user_id: str, goal_id: str, milestone_id: str) -> Optional[GoalMilestone]:
        goals = cls.list_user_goals(user_id)
        for g in goals:
            if g.goal_id == goal_id:
                for m in g.milestones:
                    if m.milestone_id == milestone_id:
                        m.is_completed = True
                        m.completed_at_ms = int(time.time() * 1000)
                        # If all milestones completed, complete goal
                        if all(ms.is_completed for ms in g.milestones):
                            g.status = GoalStatus.COMPLETED
                        return m
        return None

    @classmethod
    def archive_goal(cls, user_id: str, goal_id: str) -> Optional[Goal]:
        """
        Gently archives a goal without failure labeling or guilt induction.
        """
        goals = cls._goals.get(user_id, [])
        for g in goals:
            if g.goal_id == goal_id:
                g.status = GoalStatus.ARCHIVED
                g.updated_at_ms = int(time.time() * 1000)
                return g
        return None

    @classmethod
    def clear(cls) -> None:
        cls._goals.clear()
