"""统计服务。"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.person_project import PersonProject
from app.models.enums import PersonProjectStatus
from app.models.project import Project
from app.models.enterprise import Enterprise
from app.models.person import Person
from app.models.enums import FailReason


class StatisticsService:
    """统计服务类。"""

    def _calculate_rate(self, count: int, total: int) -> float:
        """计算比率(保留 2 位小数)。"""
        if total == 0:
            return 0.0
        return round(count / total * 100, 2)

    async def get_project_funnel(
        self, session: AsyncSession, project_id: int
    ) -> dict[str, Any]:
        """获取项目漏斗数据(漏斗转化率统计)。"""
        # 统计各状态人数
        result = await session.execute(
            select(
                PersonProject.status,
                func.count().label("count"),
            )
            .where(PersonProject.project_id == project_id)
            .group_by(PersonProject.status)
        )

        status_counts = {}
        for row in result:
            status_counts[row.status] = row.count

        # 计算转化率
        total = sum(status_counts.values())
        signed_up = status_counts.get(PersonProjectStatus.SIGNED_UP, 0)
        invited_count = status_counts.get(PersonProjectStatus.INVITED, 0)
        interview_pending_count = status_counts.get(PersonProjectStatus.INTERVIEW_PENDING, 0)
        interviewed_count = status_counts.get(PersonProjectStatus.INTERVIEWED, 0)
        in_trial_count = status_counts.get(PersonProjectStatus.IN_TRIAL, 0)
        trial_passed_count = status_counts.get(PersonProjectStatus.TRIAL_PASSED, 0)
        failed_count = status_counts.get(PersonProjectStatus.FAILED, 0)
        unreachable_count = status_counts.get(PersonProjectStatus.UNREACHABLE, 0)

        # 计算转化率
        conversion_rates = {
            "invite_rate": self._calculate_rate(invited_count, signed_up),
            "interview_rate": self._calculate_rate(
                interviewed_count, interview_pending_count
            ),
            "trial_rate": self._calculate_rate(in_trial_count, interviewed_count),
            "hire_rate": self._calculate_rate(trial_passed_count, in_trial_count),
        }

        return {
            "total": total,
            "status_counts": {
                status.value: count
                for status, count in status_counts.items()
            },
            "conversion_rates": conversion_rates,
        }

    async def get_daily_statistics(
        self, session: AsyncSession, project_id: int, date: datetime
    ) -> dict[str, Any]:
        """获取每日统计数据。"""
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = datetime(date.year, date.month, date.day, 1) + timedelta(days=1)

        # 获取当日的人员-项目关联
        result = await session.execute(
            select(
                PersonProject.status,
                func.count().label("count"),
            )
            .where(
                PersonProject.project_id == project_id,
                func.date(PersonProject.created_at) >= start_of_day,
                func.date(PersonProject.created_at) < end_of_day,
            )
            .group_by(PersonProject.status)
        )

        status_counts = {}
        for row in result:
            status_counts[row.status] = row.count

        return {
            "date": date.isoformat(),
            "total": sum(status_counts.values()),
            "status_counts": {
                status.value: count
                for status, count in status_counts.items()
            },
        }

    async def get_date_range_statistics(
        self,
        session: AsyncSession,
        project_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """获取日期范围统计数据。"""
        result = await session.execute(
            select(
                func.date(PersonProject.created_at).label("date"),
                func.count().label("count"),
            )
            .where(
                PersonProject.project_id == project_id,
                PersonProject.created_at >= start_date,
                PersonProject.created_at < end_date,
            )
            .order_by(PersonProject.created_at.asc())
        )

        # 按日期分组
        daily_stats = {}
        for row in result:
            daily_stats[str(row.date)] = row.count

        return {
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total": sum(daily_stats.values()),
            "daily_stats": daily_stats,
        }

    async def get_fail_reason_breakdown(
        self, session: AsyncSession, project_id: int
    ) -> dict[FailReason, int]:
        """获取失败原因分布。 """
        result = await session.execute(
            select(
                PersonProject.fail_reason,
                func.count().label("count"),
            )
            .where(
                PersonProject.project_id == project_id,
                PersonProject.fail_reason.is_not(None),
            )
            .group_by(PersonProject.fail_reason)
        )

        breakdown = {}
        for row in result:
            if row.fail_reason:
                breakdown[row.fail_reason] = row.count

        return breakdown
