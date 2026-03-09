"""提醒服务。"""

from datetime import datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ReminderStatus
from app.models.reminder import Reminder
from app.schemas.reminder import ReminderCreate, ReminderUpdate


class ReminderService:
    """提醒服务类。"""

    async def create(
        self,
        session: AsyncSession,
        reminder_data: ReminderCreate,
    ) -> Reminder:
        """创建提醒。"""
        reminder = Reminder(
            person_project_id=reminder_data.person_project_id,
            follow_up_id=reminder_data.follow_up_id,
            remind_time=reminder_data.remind_time,
            content=reminder_data.content,
            status=ReminderStatus.PENDING,
            created_by=reminder_data.created_by,
        )
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)
        return reminder

    async def get_by_id(self, session: AsyncSession, reminder_id: int) -> Reminder | None:
        """根据 ID 获取提醒。"""
        result = await session.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        person_project_id: int | None = None,
        status: ReminderStatus | None = None,
        created_by: int | None = None,
    ) -> tuple[list[Reminder], int]:
        """获取提醒列表。"""
        query = select(Reminder)

        # 筛选条件
        if person_project_id:
            query = query.where(Reminder.person_project_id == person_project_id)
        if status:
            query = query.where(Reminder.status == status)
        if created_by:
            query = query.where(Reminder.created_by == created_by)

        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(Reminder.remind_time.asc()).offset(skip).limit(limit)
        result = await session.execute(query)
        reminders = list(result.scalars().all())

        return reminders, total

    async def update(
        self,
        session: AsyncSession,
        reminder_id: int,
        reminder_data: ReminderUpdate,
    ) -> Reminder | None:
        """更新提醒状态。"""
        reminder = await self.get_by_id(session, reminder_id)
        if not reminder:
            return None

        reminder.status = reminder_data.status

        await session.commit()
        await session.refresh(reminder)
        return reminder

    async def delete(self, session: AsyncSession, reminder_id: int) -> bool:
        """删除提醒。"""
        reminder = await self.get_by_id(session, reminder_id)
        if not reminder:
            return False

        await session.delete(reminder)
        await session.commit()
        return True

    # ==================== 业务逻辑方法 ====================

    async def get_due_reminders(self, session: AsyncSession) -> list[Reminder]:
        """获取到期提醒（已到提醒时间且待处理）。"""
        now = datetime.now()
        result = await session.execute(
            select(Reminder)
            .where(
                Reminder.remind_time <= now,
                Reminder.status == ReminderStatus.PENDING,
            )
            .order_by(Reminder.remind_time.asc())
        )
        return list(result.scalars().all())

    async def get_upcoming_reminders(
        self, session: AsyncSession, minutes: int = 30
    ) -> list[Reminder]:
        """获取即将到期的提醒（在指定分钟内到期且待处理）。"""
        now = datetime.now()
        end_time = now + timedelta(minutes=minutes)
        result = await session.execute(
            select(Reminder)
            .where(
                Reminder.remind_time > now,
                Reminder.remind_time <= end_time,
                Reminder.status == ReminderStatus.PENDING,
            )
            .order_by(Reminder.remind_time.asc())
        )
        return list(result.scalars().all())
