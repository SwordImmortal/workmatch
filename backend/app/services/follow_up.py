"""跟进记录服务。"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.follow_up import FollowUp
from app.models.person_project import PersonProject
from app.schemas.follow_up import FollowUpCreate


class FollowUpService:
    """跟进记录服务类。"""

    async def create(
        self,
        session: AsyncSession,
        follow_up_data: FollowUpCreate,
        created_by: int,
    ) -> FollowUp:
        """创建跟进记录。"""
        follow_up = FollowUp(
            person_project_id=follow_up_data.person_project_id,
            content=follow_up_data.content,
            next_follow_time=follow_up_data.next_follow_time,
            created_by=created_by,
        )
        session.add(follow_up)
        await session.commit()
        await session.refresh(follow_up)
        return follow_up

    async def get_by_id(self, session: AsyncSession, follow_up_id: int) -> FollowUp | None:
        """根据 ID 获取跟进记录。"""
        result = await session.execute(
            select(FollowUp).where(FollowUp.id == follow_up_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        person_project_id: int | None = None,
        created_by: int | None = None,
    ) -> tuple[list[FollowUp], int]:
        """获取跟进记录列表。"""
        query = select(FollowUp)

        # 筛选条件
        if person_project_id:
            query = query.where(FollowUp.person_project_id == person_project_id)
        if created_by:
            query = query.where(FollowUp.created_by == created_by)

        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # 分页（按创建时间倒序）
        query = query.order_by(FollowUp.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        follow_ups = list(result.scalars().all())

        return follow_ups, total

    async def delete(self, session: AsyncSession, follow_up_id: int) -> bool:
        """删除跟进记录。"""
        follow_up = await self.get_by_id(session, follow_up_id)
        if not follow_up:
            return False

        await session.delete(follow_up)
        await session.commit()
        return True

    async def get_recent(
        self, session: AsyncSession, person_project_id: int, limit: int = 5
    ) -> list[FollowUp]:
        """获取最近的跟进记录。"""
        result = await session.execute(
            select(FollowUp)
            .where(FollowUp.person_project_id == person_project_id)
            .order_by(FollowUp.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending(
        self, session: AsyncSession, owner_id: int
    ) -> list[tuple[FollowUp, PersonProject]]:
        """获取待跟进记录（有下次跟进时间且未过期）。

        返回跟进记录和对应的人员-项目关联。
        """
        now = datetime.now()
        result = await session.execute(
            select(FollowUp, PersonProject)
            .join(PersonProject, FollowUp.person_project_id == PersonProject.id)
            .where(
                FollowUp.next_follow_time.is_not(None),
                FollowUp.next_follow_time > now,
                PersonProject.owner_id == owner_id,
            )
            .order_by(FollowUp.next_follow_time.asc())
        )
        return list(result.all())
