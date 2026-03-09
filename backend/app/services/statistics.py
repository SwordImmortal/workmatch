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
from app.models.reminder import Reminder
from app.models.enums import FailReason, ReminderStatus


class StatisticsService:
    """统计服务类。"""

    async def get_overview(
        self,
        session: AsyncSession,
        project_id: int | None = None,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """获取整体概览统计。"""
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = datetime(now.year, now.month, 1)

        # 基础查询条件
        pp_base = select(PersonProject)
        if project_id:
            pp_base = pp_base.where(PersonProject.project_id == project_id)
        if user_id:
            pp_base = pp_base.where(PersonProject.owner_id == user_id)

        # 1. 总人数统计（人员-项目关联数）
        total_result = await session.execute(
            select(func.count()).select_from(pp_base.subquery())
        )
        total_persons = total_result.scalar() or 0

        # 2. 时间维度统计
        today_result = await session.execute(
            select(func.count()).select_from(
                pp_base.where(PersonProject.created_at >= today_start).subquery()
            )
        )
        today_new = today_result.scalar() or 0

        week_result = await session.execute(
            select(func.count()).select_from(
                pp_base.where(PersonProject.created_at >= week_start).subquery()
            )
        )
        week_new = week_result.scalar() or 0

        month_result = await session.execute(
            select(func.count()).select_from(
                pp_base.where(PersonProject.created_at >= month_start).subquery()
            )
        )
        month_new = month_result.scalar() or 0

        # 3. 各状态分组统计
        status_result = await session.execute(
            select(
                PersonProject.status,
                func.count().label("count"),
            )
            .select_from(pp_base.subquery())
            .group_by(PersonProject.status)
        )
        status_breakdown = {}
        passed_count = 0
        for row in status_result:
            status_breakdown[row.status.value] = row.count
            if row.status == PersonProjectStatus.TRIAL_PASSED:
                passed_count = row.count

        # 4. 转化率（通过率）
        conversion_rate = self._calculate_rate(passed_count, total_persons)

        # 5. 待处理提醒数量
        reminder_query = select(func.count()).where(
            Reminder.status == ReminderStatus.PENDING
        )
        if user_id:
            reminder_query = reminder_query.where(Reminder.created_by == user_id)
        reminder_result = await session.execute(reminder_query)
        pending_reminders = reminder_result.scalar() or 0

        # 6. 按项目分组统计（如未指定项目）
        project_stats = []
        if not project_id:
            project_result = await session.execute(
                select(
                    Project.id.label("project_id"),
                    Project.name.label("project_name"),
                    func.count(PersonProject.id).label("total"),
                    func.sum(
                        case(
                            (PersonProject.status == PersonProjectStatus.TRIAL_PASSED, 1),
                            else_=0,
                        )
                    ).label("passed"),
                )
                .select_from(Project)
                .outerjoin(
                    PersonProject,
                    Project.id == PersonProject.project_id
                )
                .group_by(Project.id, Project.name)
                .order_by(func.count(PersonProject.id).desc())
                .limit(10)
            )
            for row in project_result:
                project_stats.append({
                    "project_id": row.project_id,
                    "project_name": row.project_name,
                    "total": row.total or 0,
                    "passed": int(row.passed or 0),
                })

        return {
            "total_persons": total_persons,
            "today_new": today_new,
            "week_new": week_new,
            "month_new": month_new,
            "status_breakdown": status_breakdown,
            "conversion_rate": conversion_rate,
            "pending_reminders": pending_reminders,
            "project_stats": project_stats,
        }

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
