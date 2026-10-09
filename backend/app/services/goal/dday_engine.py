from datetime import datetime, date
from typing import Optional, List
from app.domain.goal.goal import DDayInfo

class DDayEngine:
    """
    Computes accurate D-Day milestones (e.g. D-30, D-7, D-1, Today, D+N) for user goals and life events.
    """

    @classmethod
    def calculate_dday(cls, title: str, target_date_str: str) -> Optional[DDayInfo]:
        try:
            target_dt = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

        today = date.today()
        delta_days = (target_dt - today).days

        if delta_days == 0:
            tag = "D-Day (Today)"
        elif delta_days > 0:
            tag = f"D-{delta_days}"
        else:
            tag = f"D+{-delta_days}"

        return DDayInfo(
            title=title,
            target_date_str=target_date_str,
            days_remaining=delta_days,
            dday_tag=tag
        )
