"""统计相关 schemas。"""

from pydantic import BaseModel


class ProjectStatsItem(BaseModel):
    """项目统计项。"""

    project_id: int
    project_name: str
    total: int
    passed: int


class OverviewStats(BaseModel):
    """整体概览统计。"""

    total_persons: int
    today_new: int
    week_new: int
    month_new: int
    status_breakdown: dict[str, int]
    conversion_rate: float
    pending_reminders: int
    project_stats: list[ProjectStatsItem]
