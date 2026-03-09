"""人员-项目关联服务。"""

from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.person_project import PersonProject
from app.models.status_history import StatusHistory
from app.models.enums import FailReason, PersonProjectStatus
from app.schemas.person_project import PersonProjectCreate


# 状态流转规则：定义允许的下一步状态
VALID_TRANSITIONS = {
    PersonProjectStatus.SIGNED_UP: [
        PersonProjectStatus.INVITED,
        PersonProjectStatus.FAILED,
        PersonProjectStatus.UNREACHABLE,
    ],
    PersonProjectStatus.INVITED: [
        PersonProjectStatus.INTERVIEW_PENDING,
        PersonProjectStatus.FAILED,
        PersonProjectStatus.UNREACHABLE,
    ],
    PersonProjectStatus.INTERVIEW_PENDING: [
        PersonProjectStatus.INTERVIEWED,
        PersonProjectStatus.FAILED,
        PersonProjectStatus.UNREACHABLE,
    ],
    PersonProjectStatus.INTERVIEWED: [
        PersonProjectStatus.IN_TRIAL,
        PersonProjectStatus.FAILED,
        PersonProjectStatus.UNREACHABLE,
    ],
    PersonProjectStatus.IN_TRIAL: [
        PersonProjectStatus.TRIAL_PASSED,
        PersonProjectStatus.FAILED,
        PersonProjectStatus.UNREACHABLE,
    ],
    PersonProjectStatus.TRIAL_PASSED: [],  # 终态，不可再变
    PersonProjectStatus.FAILED: [],  # 终态
    PersonProjectStatus.UNREACHABLE: [],  # 终态
}


class PersonProjectService:
    """人员-项目关联服务类。"""

    async def create(
        self, session: AsyncSession, pp_data: PersonProjectCreate
    ) -> PersonProject:
        """创建人员-项目关联（分配人员到项目）。"""
        # 检查是否已存在关联
        existing = await session.execute(
            select(PersonProject).where(
                PersonProject.person_id == pp_data.person_id,
                PersonProject.project_id == pp_data.project_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("该人员已分配到此项目")

        pp = PersonProject(
            person_id=pp_data.person_id,
            project_id=pp_data.project_id,
            owner_id=pp_data.owner_id,
            status=PersonProjectStatus.SIGNED_UP,
        )
        session.add(pp)
        await session.commit()
        await session.refresh(pp)
        return pp

    async def get_by_id(self, session: AsyncSession, pp_id: int) -> PersonProject | None:
        """根据 ID 获取人员-项目关联。"""
        result = await session.execute(
            select(PersonProject).where(PersonProject.id == pp_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        project_id: int | None = None,
        person_id: int | None = None,
        status: PersonProjectStatus | None = None,
        owner_id: int | None = None,
    ) -> tuple[list[PersonProject], int]:
        """获取人员-项目关联列表。"""
        query = select(PersonProject)

        # 筛选条件
        if project_id:
            query = query.where(PersonProject.project_id == project_id)
        if person_id:
            query = query.where(PersonProject.person_id == person_id)
        if status:
            query = query.where(PersonProject.status == status)
        if owner_id:
            query = query.where(PersonProject.owner_id == owner_id)

        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(PersonProject.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        pps = list(result.scalars().all())

        return pps, total

    async def advance_status(
        self,
        session: AsyncSession,
        pp_id: int,
        to_status: PersonProjectStatus,
        changed_by: int,
        fail_reason: FailReason | None = None,
        fail_remark: str | None = None,
    ) -> PersonProject | None:
        """推进状态流转。"""
        pp = await self.get_by_id(session, pp_id)
        if not pp:
            return None

        from_status = pp.status

        # 验证失败状态必须提供原因
        if to_status == PersonProjectStatus.FAILED and not fail_reason:
            raise ValueError("失败状态必须提供失败原因")

        # 验证 fail_remark 必须配合 fail_reason 使用
        if fail_remark and not fail_reason:
            raise ValueError("失败备注必须配合失败原因使用")

        # 验证状态流转是否合法
        if to_status not in VALID_TRANSITIONS.get(from_status, []):
            raise ValueError(f"非法状态流转: {from_status.value} -> {to_status.value}")

        # 更新状态
        pp.status = to_status
        if fail_reason:
            pp.fail_reason = fail_reason
        if fail_remark:
            pp.fail_remark = fail_remark

        # 创建状态变更历史
        history = StatusHistory(
            person_project_id=pp_id,
            from_status=from_status,
            to_status=to_status,
            changed_at=datetime.now(),
            changed_by=changed_by,
        )
        session.add(history)

        await session.commit()
        await session.refresh(pp)
        return pp

    async def get_status_history(
        self, session: AsyncSession, pp_id: int
    ) -> list[StatusHistory]:
        """获取状态变更历史。"""
        result = await session.execute(
            select(StatusHistory)
            .where(StatusHistory.person_project_id == pp_id)
            .order_by(StatusHistory.changed_at.asc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        pp_id: int,
        attended_training: bool | None = None,
        purchased_package: bool | None = None,
        completed_rooms: int | None = None,
    ) -> PersonProject | None:
        """更新人员-项目关联信息（专用字段）。"""
        pp = await self.get_by_id(session, pp_id)
        if not pp:
            return None

        if attended_training is not None:
            pp.attended_training = attended_training
        if purchased_package is not None:
            pp.purchased_package = purchased_package
        if completed_rooms is not None:
            pp.completed_rooms = completed_rooms

        await session.commit()
        await session.refresh(pp)
        return pp

    async def get_project_statistics(
        self, session: AsyncSession, project_id: int
    ) -> dict:
        """获取项目统计。"""
        # 统计各状态人数
        result = await session.execute(
            select(
                func.count().label("total"),
                func.sum(
                    case((PersonProject.status == PersonProjectStatus.SIGNED_UP, 1), else_=0)
                ).label("signed_up"),
                func.sum(
                    case((PersonProject.status == PersonProjectStatus.INVITED, 1), else_=0)
                ).label("invited"),
                func.sum(
                    case((PersonProject.status == PersonProjectStatus.INTERVIEW_PENDING, 1), else_=0)
                ).label("interview_pending"),
                func.sum(
                    case((PersonProject.status == PersonProjectStatus.INTERVIEWED, 1), else_=0)
                ).label("interviewed"),
                func.sum(
                    case((PersonProject.status == PersonProjectStatus.IN_TRIAL, 1), else_=0)
                ).label("in_trial"),
                func.sum(
                    case((PersonProject.status == PersonProjectStatus.TRIAL_PASSED, 1), else_=0)
                ).label("trial_passed"),
                func.sum(
                    case((PersonProject.status == PersonProjectStatus.FAILED, 1), else_=0)
                ).label("failed"),
                func.sum(
                    case((PersonProject.status == PersonProjectStatus.UNREACHABLE, 1), else_=0)
                ).label("unreachable"),
            ).where(PersonProject.project_id == project_id)
        )
        row = result.one()

        return {
            "project_id": project_id,
            "total": row.total or 0,
            "status_breakdown": {
                "signed_up": row.signed_up or 0,
                "invited": row.invited or 0,
                "interview_pending": row.interview_pending or 0,
                "interviewed": row.interviewed or 0,
                "in_trial": row.in_trial or 0,
                "trial_passed": row.trial_passed or 0,
                "failed": row.failed or 0,
                "unreachable": row.unreachable or 0,
            },
        }
