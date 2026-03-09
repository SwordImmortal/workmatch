"""ReminderService 单元测试。"""

import pytest
from datetime import datetime, timedelta

from app.models.enums import ReminderStatus
from app.schemas.enterprise import EnterpriseCreate
from app.schemas.person import PersonCreate
from app.schemas.person_project import PersonProjectCreate
from app.schemas.project import ProjectCreate
from app.schemas.reminder import ReminderCreate, ReminderUpdate
from app.services.enterprise import EnterpriseService
from app.services.person import PersonService
from app.services.person_project import PersonProjectService
from app.services.project import ProjectService
from app.services.reminder import ReminderService


class TestReminderService:
    """ReminderService 单元测试。"""

    @pytest.fixture
    async def setup_data(self, db_session):
        """创建测试数据。"""
        enterprise_service = EnterpriseService()
        project_service = ProjectService()
        person_service = PersonService()
        pp_service = PersonProjectService()
        reminder_service = ReminderService()

        # 创建企业
        enterprise = await enterprise_service.create(
            db_session, EnterpriseCreate(name="测试企业")
        )

        # 创建项目
        project = await project_service.create(
            db_session,
            ProjectCreate(
                name="测试项目",
                enterprise_id=enterprise.id,
                job_title="配送员",
            ),
        )

        # 创建人员
        person = await person_service.create(
            db_session,
            PersonCreate(name="张三", phone="13800138000", city="北京"),
            created_by=1,
        )

        # 创建人员-项目关联
        pp = await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=person.id,
                project_id=project.id,
                owner_id=1,
            ),
        )

        return {
            "enterprise": enterprise,
            "project": project,
            "person": person,
            "pp": pp,
            "pp_service": pp_service,
            "reminder_service": reminder_service,
        }

    # ==================== CRUD 测试 ====================

    @pytest.mark.asyncio
    async def test_create_reminder(self, db_session, setup_data):
        """测试创建提醒。"""
        data = setup_data
        reminder_data = ReminderCreate(
            person_project_id=data["pp"].id,
            remind_time=datetime.now() + timedelta(hours=2),
            content="下午2点面试提醒",
            created_by=1,
        )

        reminder = await data["reminder_service"].create(
            db_session, reminder_data
        )

        assert reminder.id is not None
        assert reminder.content == "下午2点面试提醒"
        assert reminder.status == ReminderStatus.PENDING

    @pytest.mark.asyncio
    async def test_create_reminder_with_follow_up(self, db_session, setup_data):
        """测试创建关联跟进记录的提醒。"""
        data = setup_data

        # 先创建跟进记录
        from app.schemas.follow_up import FollowUpCreate
        from app.services.follow_up import FollowUpService

        follow_up_service = FollowUpService()
        follow_up = await follow_up_service.create(
            db_session,
            FollowUpCreate(
                person_project_id=data["pp"].id,
                content="预约了面试",
                next_follow_time=datetime.now() + timedelta(days=1),
            ),
            created_by=1,
        )

        reminder_data = ReminderCreate(
            person_project_id=data["pp"].id,
            follow_up_id=follow_up.id,
            remind_time=datetime.now() + timedelta(hours=2),
            content="面试前提醒",
            created_by=1,
        )

        reminder = await data["reminder_service"].create(
            db_session, reminder_data
        )

        assert reminder.follow_up_id == follow_up.id

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session, setup_data):
        """测试根据 ID 获取提醒。"""
        data = setup_data
        reminder_data = ReminderCreate(
            person_project_id=data["pp"].id,
            remind_time=datetime.now() + timedelta(hours=1),
            content="测试提醒",
            created_by=1,
        )
        created = await data["reminder_service"].create(
            db_session, reminder_data
        )

        reminder = await data["reminder_service"].get_by_id(db_session, created.id)

        assert reminder is not None
        assert reminder.id == created.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """测试获取不存在的提醒返回 None。"""
        service = ReminderService()
        reminder = await service.get_by_id(db_session, 999)
        assert reminder is None

    @pytest.mark.asyncio
    async def test_get_list_by_person_project(self, db_session, setup_data):
        """测试按人员-项目获取提醒列表。"""
        data = setup_data

        # 创建多条提醒
        for i in range(3):
            await data["reminder_service"].create(
                db_session,
                ReminderCreate(
                    person_project_id=data["pp"].id,
                    remind_time=datetime.now() + timedelta(hours=i + 1),
                    content=f"提醒{i}",
                    created_by=1,
                ),
            )

        reminders, total = await data["reminder_service"].get_list(
            db_session, person_project_id=data["pp"].id
        )

        assert len(reminders) == 3
        assert total == 3

    @pytest.mark.asyncio
    async def test_get_list_by_status(self, db_session, setup_data):
        """测试按状态获取提醒列表。"""
        data = setup_data

        # 创建待处理提醒
        r1 = await data["reminder_service"].create(
            db_session,
            ReminderCreate(
                person_project_id=data["pp"].id,
                remind_time=datetime.now() + timedelta(hours=1),
                content="待处理提醒",
                created_by=1,
            ),
        )

        # 创建并完成一个提醒
        r2 = await data["reminder_service"].create(
            db_session,
            ReminderCreate(
                person_project_id=data["pp"].id,
                remind_time=datetime.now() + timedelta(hours=1),
                content="已完成提醒",
                created_by=1,
            ),
        )
        await data["reminder_service"].update(
            db_session, r2.id, ReminderUpdate(status=ReminderStatus.COMPLETED)
        )

        pending, total = await data["reminder_service"].get_list(
            db_session, status=ReminderStatus.PENDING
        )

        assert len(pending) == 1
        assert pending[0].status == ReminderStatus.PENDING

    # ==================== 状态更新测试 ====================

    @pytest.mark.asyncio
    async def test_mark_completed(self, db_session, setup_data):
        """测试标记提醒完成。"""
        data = setup_data
        reminder_data = ReminderCreate(
            person_project_id=data["pp"].id,
            remind_time=datetime.now() + timedelta(hours=1),
            content="测试提醒",
            created_by=1,
        )
        created = await data["reminder_service"].create(
            db_session, reminder_data
        )

        updated = await data["reminder_service"].update(
            db_session, created.id, ReminderUpdate(status=ReminderStatus.COMPLETED)
        )

        assert updated.status == ReminderStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_mark_ignored(self, db_session, setup_data):
        """测试标记提醒忽略。"""
        data = setup_data
        reminder_data = ReminderCreate(
            person_project_id=data["pp"].id,
            remind_time=datetime.now() + timedelta(hours=1),
            content="测试提醒",
            created_by=1,
        )
        created = await data["reminder_service"].create(
            db_session, reminder_data
        )

        updated = await data["reminder_service"].update(
            db_session, created.id, ReminderUpdate(status=ReminderStatus.IGNORED)
        )

        assert updated.status == ReminderStatus.IGNORED

    @pytest.mark.asyncio
    async def test_update_not_found(self, db_session):
        """测试更新不存在的提醒返回 None。"""
        service = ReminderService()
        result = await service.update(
            db_session, 999, ReminderUpdate(status=ReminderStatus.COMPLETED)
        )
        assert result is None

    # ==================== 删除测试 ====================

    @pytest.mark.asyncio
    async def test_delete_reminder(self, db_session, setup_data):
        """测试删除提醒。"""
        data = setup_data
        reminder_data = ReminderCreate(
            person_project_id=data["pp"].id,
            remind_time=datetime.now() + timedelta(hours=1),
            content="测试提醒",
            created_by=1,
        )
        created = await data["reminder_service"].create(
            db_session, reminder_data
        )

        result = await data["reminder_service"].delete(db_session, created.id)

        assert result is True
        reminder = await data["reminder_service"].get_by_id(db_session, created.id)
        assert reminder is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session):
        """测试删除不存在的提醒返回 False。"""
        service = ReminderService()
        result = await service.delete(db_session, 999)
        assert result is False

    # ==================== 业务逻辑测试 ====================

    @pytest.mark.asyncio
    async def test_get_due_reminders(self, db_session, setup_data):
        """测试获取到期提醒。"""
        data = setup_data

        # 创建已到期的提醒
        await data["reminder_service"].create(
            db_session,
            ReminderCreate(
                person_project_id=data["pp"].id,
                remind_time=datetime.now() - timedelta(minutes=30),  # 30分钟前到期
                content="已到期提醒",
                created_by=1,
            ),
        )

        # 创建未到期的提醒
        await data["reminder_service"].create(
            db_session,
            ReminderCreate(
                person_project_id=data["pp"].id,
                remind_time=datetime.now() + timedelta(hours=1),  # 1小时后到期
                content="未到期提醒",
                created_by=1,
            ),
        )

        due = await data["reminder_service"].get_due_reminders(db_session)

        # 应该只返回已到期且待处理的提醒
        assert len(due) == 1
        assert due[0].content == "已到期提醒"

    @pytest.mark.asyncio
    async def test_get_due_reminders_exclude_completed(self, db_session, setup_data):
        """测试到期提醒不包含已完成的。"""
        data = setup_data

        # 创建已到期的提醒
        r1 = await data["reminder_service"].create(
            db_session,
            ReminderCreate(
                person_project_id=data["pp"].id,
                remind_time=datetime.now() - timedelta(minutes=30),
                content="已完成提醒",
                created_by=1,
            ),
        )

        # 标记为完成
        await data["reminder_service"].update(
            db_session, r1.id, ReminderUpdate(status=ReminderStatus.COMPLETED)
        )

        due = await data["reminder_service"].get_due_reminders(db_session)

        # 已完成的提醒不应出现在到期列表
        assert len(due) == 0

    @pytest.mark.asyncio
    async def test_get_upcoming_reminders(self, db_session, setup_data):
        """测试获取即将到期的提醒。"""
        data = setup_data

        # 创建即将到期的提醒（15分钟后）
        await data["reminder_service"].create(
            db_session,
            ReminderCreate(
                person_project_id=data["pp"].id,
                remind_time=datetime.now() + timedelta(minutes=15),
                content="即将到期提醒",
                created_by=1,
            ),
        )

        # 创建较远将来的提醒（2小时后）
        await data["reminder_service"].create(
            db_session,
            ReminderCreate(
                person_project_id=data["pp"].id,
                remind_time=datetime.now() + timedelta(hours=2),
                content="较远提醒",
                created_by=1,
            ),
        )

        # 获取30分钟内到期的提醒
        upcoming = await data["reminder_service"].get_upcoming_reminders(
            db_session, minutes=30
        )

        assert len(upcoming) == 1
        assert upcoming[0].content == "即将到期提醒"

    @pytest.mark.asyncio
    async def test_get_reminders_by_user(self, db_session, setup_data):
        """测试获取用户创建的提醒。"""
        data = setup_data

        # 创建用户1的提醒
        await data["reminder_service"].create(
            db_session,
            ReminderCreate(
                person_project_id=data["pp"].id,
                remind_time=datetime.now() + timedelta(hours=1),
                content="用户1的提醒",
                created_by=1,
            ),
        )

        reminders, total = await data["reminder_service"].get_list(
            db_session, created_by=1
        )

        assert len(reminders) == 1
        assert reminders[0].created_by == 1
