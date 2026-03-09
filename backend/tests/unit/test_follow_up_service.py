"""FollowUpService 单元测试。"""

import pytest
from datetime import datetime, timedelta

from app.schemas.enterprise import EnterpriseCreate
from app.schemas.person import PersonCreate
from app.schemas.person_project import PersonProjectCreate
from app.schemas.project import ProjectCreate
from app.schemas.follow_up import FollowUpCreate
from app.services.enterprise import EnterpriseService
from app.services.person import PersonService
from app.services.person_project import PersonProjectService
from app.services.project import ProjectService


class TestFollowUpService:
    """FollowUpService 单元测试。"""

    @pytest.fixture
    async def setup_data(self, db_session):
        """创建测试数据。"""
        from app.services.follow_up import FollowUpService

        enterprise_service = EnterpriseService()
        project_service = ProjectService()
        person_service = PersonService()
        pp_service = PersonProjectService()
        follow_up_service = FollowUpService()

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
            "follow_up_service": follow_up_service,
        }

    # ==================== CRUD 测试 ====================

    @pytest.mark.asyncio
    async def test_create_follow_up(self, db_session, setup_data):
        """测试创建跟进记录。"""
        data = setup_data
        follow_up_data = FollowUpCreate(
            person_project_id=data["pp"].id,
            content="电话沟通，候选人对岗位感兴趣",
            next_follow_time=datetime.now() + timedelta(days=1),
        )

        follow_up = await data["follow_up_service"].create(
            db_session, follow_up_data, created_by=1
        )

        assert follow_up.id is not None
        assert follow_up.content == "电话沟通，候选人对岗位感兴趣"
        assert follow_up.next_follow_time is not None

    @pytest.mark.asyncio
    async def test_create_follow_up_without_next_time(self, db_session, setup_data):
        """测试创建跟进记录不设置下次跟进时间。"""
        data = setup_data
        follow_up_data = FollowUpCreate(
            person_project_id=data["pp"].id,
            content="已发送岗位介绍",
        )

        follow_up = await data["follow_up_service"].create(
            db_session, follow_up_data, created_by=1
        )

        assert follow_up.id is not None
        assert follow_up.next_follow_time is None

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session, setup_data):
        """测试根据 ID 获取跟进记录。"""
        data = setup_data
        follow_up_data = FollowUpCreate(
            person_project_id=data["pp"].id,
            content="测试跟进",
        )
        created = await data["follow_up_service"].create(
            db_session, follow_up_data, created_by=1
        )

        follow_up = await data["follow_up_service"].get_by_id(db_session, created.id)

        assert follow_up is not None
        assert follow_up.id == created.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """测试获取不存在的跟进记录返回 None。"""
        from app.services.follow_up import FollowUpService

        service = FollowUpService()
        follow_up = await service.get_by_id(db_session, 999)
        assert follow_up is None

    @pytest.mark.asyncio
    async def test_get_list_by_person_project(self, db_session, setup_data):
        """测试按人员-项目获取跟进记录列表。"""
        data = setup_data

        # 创建多条跟进记录
        for i in range(3):
            await data["follow_up_service"].create(
                db_session,
                FollowUpCreate(
                    person_project_id=data["pp"].id,
                    content=f"跟进记录{i}",
                ),
                created_by=1,
            )

        follow_ups, total = await data["follow_up_service"].get_list(
            db_session, person_project_id=data["pp"].id
        )

        assert len(follow_ups) == 3
        assert total == 3

    @pytest.mark.asyncio
    async def test_get_list_pagination(self, db_session, setup_data):
        """测试跟进记录分页。"""
        data = setup_data

        # 创建 5 条记录
        for i in range(5):
            await data["follow_up_service"].create(
                db_session,
                FollowUpCreate(
                    person_project_id=data["pp"].id,
                    content=f"跟进记录{i}",
                ),
                created_by=1,
            )

        follow_ups, total = await data["follow_up_service"].get_list(
            db_session, person_project_id=data["pp"].id, skip=0, limit=3
        )

        assert len(follow_ups) == 3
        assert total == 5

    @pytest.mark.asyncio
    async def test_delete_follow_up(self, db_session, setup_data):
        """测试删除跟进记录。"""
        data = setup_data
        follow_up_data = FollowUpCreate(
            person_project_id=data["pp"].id,
            content="测试跟进",
        )
        created = await data["follow_up_service"].create(
            db_session, follow_up_data, created_by=1
        )

        result = await data["follow_up_service"].delete(db_session, created.id)

        assert result is True
        follow_up = await data["follow_up_service"].get_by_id(db_session, created.id)
        assert follow_up is None

    @pytest.mark.asyncio
    async def test_delete_follow_up_not_found(self, db_session):
        """测试删除不存在的跟进记录返回 False。"""
        from app.services.follow_up import FollowUpService

        service = FollowUpService()
        result = await service.delete(db_session, 999)
        assert result is False

    # ==================== 业务逻辑测试 ====================

    @pytest.mark.asyncio
    async def test_get_recent_follow_ups(self, db_session, setup_data):
        """测试获取最近跟进记录。"""
        data = setup_data

        # 创建多条跟进记录
        for i in range(3):
            await data["follow_up_service"].create(
                db_session,
                FollowUpCreate(
                    person_project_id=data["pp"].id,
                    content=f"跟进记录{i}",
                ),
                created_by=1,
            )

        recent = await data["follow_up_service"].get_recent(
            db_session, data["pp"].id, limit=2
        )

        # 验证返回数量正确
        assert len(recent) == 2
        # 验证都是该人员-项目的跟进记录
        for r in recent:
            assert r.person_project_id == data["pp"].id

    @pytest.mark.asyncio
    async def test_get_pending_follow_ups(self, db_session, setup_data):
        """测试获取待跟进记录（有下次跟进时间且未过期）。"""
        data = setup_data

        # 创建一条有待跟进时间的记录
        await data["follow_up_service"].create(
            db_session,
            FollowUpCreate(
                person_project_id=data["pp"].id,
                content="待跟进",
                next_follow_time=datetime.now() + timedelta(days=1),
            ),
            created_by=1,
        )

        # 创建一条已过期的记录
        await data["follow_up_service"].create(
            db_session,
            FollowUpCreate(
                person_project_id=data["pp"].id,
                content="已过期",
                next_follow_time=datetime.now() - timedelta(days=1),
            ),
            created_by=1,
        )

        pending = await data["follow_up_service"].get_pending(
            db_session, owner_id=1
        )

        # 应该返回有待跟进时间且未过期的记录关联
        assert len(pending) >= 1
