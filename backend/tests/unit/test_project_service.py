"""ProjectService 单元测试。"""

import pytest
from decimal import Decimal

from app.models.enums import ProjectStatus
from app.schemas.enterprise import EnterpriseCreate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.enterprise import EnterpriseService
from app.services.project import ProjectService


class TestProjectService:
    """ProjectService 单元测试。"""

    @pytest.fixture
    async def enterprise(self, db_session):
        """创建测试企业。"""
        service = EnterpriseService()
        return await service.create(db_session, EnterpriseCreate(name="测试企业"))

    @pytest.mark.asyncio
    async def test_create_project(self, db_session, enterprise):
        """测试创建项目。"""
        service = ProjectService()
        project_data = ProjectCreate(
            name="京东配送",
            enterprise_id=enterprise.id,
            job_title="配送员",
            salary_range="8000-12000",
            work_address="北京市朝阳区",
            priority=10,
        )

        project = await service.create(db_session, project_data)

        assert project.id is not None
        assert project.name == "京东配送"
        assert project.enterprise_id == enterprise.id
        assert project.status == ProjectStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_create_project_with_unit_price(self, db_session, enterprise):
        """测试创建酒店保洁项目（带单价）。"""
        service = ProjectService()
        project_data = ProjectCreate(
            name="酒店保洁",
            enterprise_id=enterprise.id,
            job_title="保洁员",
            unit_price=Decimal("24.00"),  # 24元/间
        )

        project = await service.create(db_session, project_data)

        assert project.unit_price == Decimal("24.00")

    @pytest.mark.asyncio
    async def test_create_project_invalid_enterprise(self, db_session):
        """测试创建项目时企业不存在抛出异常。"""
        service = ProjectService()
        project_data = ProjectCreate(
            name="测试项目",
            enterprise_id=999,
            job_title="测试岗位",
        )

        with pytest.raises(ValueError, match="企业不存在"):
            await service.create(db_session, project_data)

    @pytest.mark.asyncio
    async def test_get_project_by_id(self, db_session, enterprise):
        """测试根据 ID 获取项目。"""
        service = ProjectService()
        created = await service.create(
            db_session,
            ProjectCreate(name="测试项目", enterprise_id=enterprise.id, job_title="测试岗位"),
        )

        project = await service.get_by_id(db_session, created.id)

        assert project is not None
        assert project.id == created.id

    @pytest.mark.asyncio
    async def test_get_project_by_id_not_found(self, db_session):
        """测试获取不存在的项目返回 None。"""
        service = ProjectService()

        project = await service.get_by_id(db_session, 999)

        assert project is None

    @pytest.mark.asyncio
    async def test_get_project_list(self, db_session, enterprise):
        """测试获取项目列表。"""
        service = ProjectService()

        for i in range(5):
            await service.create(
                db_session,
                ProjectCreate(
                    name=f"项目{i}",
                    enterprise_id=enterprise.id,
                    job_title=f"岗位{i}",
                ),
            )

        projects, total = await service.get_list(db_session, skip=0, limit=3)

        assert len(projects) == 3
        assert total == 5

    @pytest.mark.asyncio
    async def test_get_project_list_by_enterprise(self, db_session):
        """测试按企业筛选项目列表。"""
        enterprise_service = EnterpriseService()
        project_service = ProjectService()

        enterprise1 = await enterprise_service.create(
            db_session, EnterpriseCreate(name="企业1")
        )
        enterprise2 = await enterprise_service.create(
            db_session, EnterpriseCreate(name="企业2")
        )

        await project_service.create(
            db_session,
            ProjectCreate(name="项目1", enterprise_id=enterprise1.id, job_title="岗位"),
        )
        await project_service.create(
            db_session,
            ProjectCreate(name="项目2", enterprise_id=enterprise2.id, job_title="岗位"),
        )

        projects, total = await project_service.get_list(
            db_session, enterprise_id=enterprise1.id
        )

        assert len(projects) == 1
        assert projects[0].enterprise_id == enterprise1.id

    @pytest.mark.asyncio
    async def test_get_project_list_by_status(self, db_session, enterprise):
        """测试按状态筛选项目列表。"""
        service = ProjectService()

        await service.create(
            db_session,
            ProjectCreate(name="活跃项目", enterprise_id=enterprise.id, job_title="岗位"),
        )
        paused = await service.create(
            db_session,
            ProjectCreate(name="暂停项目", enterprise_id=enterprise.id, job_title="岗位"),
        )
        await service.update(
            db_session, paused.id, ProjectUpdate(status=ProjectStatus.PAUSED)
        )

        projects, total = await service.get_list(
            db_session, status=ProjectStatus.ACTIVE
        )

        assert len(projects) == 1
        assert projects[0].status == ProjectStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_update_project(self, db_session, enterprise):
        """测试更新项目信息。"""
        service = ProjectService()
        created = await service.create(
            db_session,
            ProjectCreate(name="测试项目", enterprise_id=enterprise.id, job_title="岗位"),
        )

        updated = await service.update(
            db_session,
            created.id,
            ProjectUpdate(
                name="更新项目名",
                salary_range="10000-15000",
                priority=20,
            ),
        )

        assert updated.name == "更新项目名"
        assert updated.salary_range == "10000-15000"
        assert updated.priority == 20

    @pytest.mark.asyncio
    async def test_update_project_status(self, db_session, enterprise):
        """测试更新项目状态。"""
        service = ProjectService()
        created = await service.create(
            db_session,
            ProjectCreate(name="测试项目", enterprise_id=enterprise.id, job_title="岗位"),
        )

        updated = await service.update(
            db_session,
            created.id,
            ProjectUpdate(status=ProjectStatus.PAUSED),
        )

        assert updated.status == ProjectStatus.PAUSED

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, db_session):
        """测试更新不存在的项目返回 None。"""
        service = ProjectService()

        updated = await service.update(
            db_session, 999, ProjectUpdate(name="新名称")
        )

        assert updated is None

    @pytest.mark.asyncio
    async def test_delete_project(self, db_session, enterprise):
        """测试删除项目。"""
        service = ProjectService()
        created = await service.create(
            db_session,
            ProjectCreate(name="测试项目", enterprise_id=enterprise.id, job_title="岗位"),
        )

        result = await service.delete(db_session, created.id)

        assert result is True
        project = await service.get_by_id(db_session, created.id)
        assert project is None

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, db_session):
        """测试删除不存在的项目返回 False。"""
        service = ProjectService()

        result = await service.delete(db_session, 999)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_project_with_enterprise(self, db_session, enterprise):
        """测试获取项目及其所属企业。"""
        service = ProjectService()
        created = await service.create(
            db_session,
            ProjectCreate(name="测试项目", enterprise_id=enterprise.id, job_title="岗位"),
        )

        project = await service.get_with_enterprise(db_session, created.id)

        assert project is not None
        assert hasattr(project, "enterprise")
        assert project.enterprise.name == "测试企业"

    @pytest.mark.asyncio
    async def test_get_project_statistics(self, db_session, enterprise):
        """测试获取项目统计。"""
        service = ProjectService()
        created = await service.create(
            db_session,
            ProjectCreate(name="测试项目", enterprise_id=enterprise.id, job_title="岗位"),
        )

        stats = await service.get_statistics(db_session, created.id)

        assert stats is not None
        assert "total_persons" in stats
        assert "status_breakdown" in stats

    @pytest.mark.asyncio
    async def test_delete_project_with_persons_blocked(self, db_session, enterprise):
        """测试有人员的项目不能删除。"""
        from app.services.person_project import PersonProjectService
        from app.schemas.person import PersonCreate
        from app.schemas.person_project import PersonProjectCreate
        from app.services.person import PersonService

        project_service = ProjectService()
        person_service = PersonService()
        pp_service = PersonProjectService()

        project = await project_service.create(
            db_session,
            ProjectCreate(name="测试项目", enterprise_id=enterprise.id, job_title="岗位"),
        )
        person = await person_service.create(
            db_session,
            PersonCreate(name="张三", phone="13800138000", city="北京"),
            created_by=1,
        )
        await pp_service.create(
            db_session,
            PersonProjectCreate(person_id=person.id, project_id=project.id, owner_id=1),
        )

        with pytest.raises(ValueError, match="该项目下存在人员"):
            await project_service.delete(db_session, project.id)
