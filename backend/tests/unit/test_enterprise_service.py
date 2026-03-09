"""EnterpriseService 单元测试。"""

import pytest

from app.models.enums import EnterpriseStatus
from app.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate
from app.services.enterprise import EnterpriseService


class TestEnterpriseService:
    """EnterpriseService 单元测试。"""

    @pytest.mark.asyncio
    async def test_create_enterprise(self, db_session):
        """测试创建企业。"""
        service = EnterpriseService()
        enterprise_data = EnterpriseCreate(
            name="测试企业",
            contact_name="张经理",
            contact_phone="13800138000",
            address="北京市朝阳区",
        )

        enterprise = await service.create(db_session, enterprise_data)

        assert enterprise.id is not None
        assert enterprise.name == "测试企业"
        assert enterprise.contact_name == "张经理"
        assert enterprise.status == EnterpriseStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_create_enterprise_duplicate_name(self, db_session):
        """测试创建重复企业名称抛出异常。"""
        service = EnterpriseService()
        enterprise_data = EnterpriseCreate(name="测试企业")

        await service.create(db_session, enterprise_data)

        with pytest.raises(ValueError, match="企业名称已存在"):
            await service.create(db_session, enterprise_data)

    @pytest.mark.asyncio
    async def test_get_enterprise_by_id(self, db_session):
        """测试根据 ID 获取企业。"""
        service = EnterpriseService()
        created = await service.create(
            db_session, EnterpriseCreate(name="测试企业")
        )

        enterprise = await service.get_by_id(db_session, created.id)

        assert enterprise is not None
        assert enterprise.id == created.id
        assert enterprise.name == "测试企业"

    @pytest.mark.asyncio
    async def test_get_enterprise_by_id_not_found(self, db_session):
        """测试获取不存在的企业返回 None。"""
        service = EnterpriseService()

        enterprise = await service.get_by_id(db_session, 999)

        assert enterprise is None

    @pytest.mark.asyncio
    async def test_get_enterprise_list(self, db_session):
        """测试获取企业列表。"""
        service = EnterpriseService()

        for i in range(5):
            await service.create(
                db_session, EnterpriseCreate(name=f"企业{i}")
            )

        enterprises, total = await service.get_list(db_session, skip=0, limit=3)

        assert len(enterprises) == 3
        assert total == 5

    @pytest.mark.asyncio
    async def test_get_enterprise_list_with_status_filter(self, db_session):
        """测试按状态筛选企业列表。"""
        service = EnterpriseService()

        await service.create(db_session, EnterpriseCreate(name="活跃企业"))
        inactive = await service.create(db_session, EnterpriseCreate(name="停用企业"))
        await service.update(db_session, inactive.id, EnterpriseUpdate(status=EnterpriseStatus.INACTIVE))

        enterprises, total = await service.get_list(
            db_session, status=EnterpriseStatus.ACTIVE
        )

        assert len(enterprises) == 1
        assert enterprises[0].status == EnterpriseStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_update_enterprise(self, db_session):
        """测试更新企业信息。"""
        service = EnterpriseService()
        created = await service.create(
            db_session, EnterpriseCreate(name="测试企业")
        )

        updated = await service.update(
            db_session,
            created.id,
            EnterpriseUpdate(contact_name="李经理", contact_phone="13900139000"),
        )

        assert updated.contact_name == "李经理"
        assert updated.contact_phone == "13900139000"
        assert updated.name == "测试企业"

    @pytest.mark.asyncio
    async def test_update_enterprise_not_found(self, db_session):
        """测试更新不存在的企业返回 None。"""
        service = EnterpriseService()

        updated = await service.update(
            db_session, 999, EnterpriseUpdate(contact_name="新联系人")
        )

        assert updated is None

    @pytest.mark.asyncio
    async def test_delete_enterprise(self, db_session):
        """测试删除企业。"""
        service = EnterpriseService()
        created = await service.create(
            db_session, EnterpriseCreate(name="测试企业")
        )

        result = await service.delete(db_session, created.id)

        assert result is True
        enterprise = await service.get_by_id(db_session, created.id)
        assert enterprise is None

    @pytest.mark.asyncio
    async def test_delete_enterprise_not_found(self, db_session):
        """测试删除不存在的企业返回 False。"""
        service = EnterpriseService()

        result = await service.delete(db_session, 999)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_enterprise_with_projects(self, db_session):
        """测试获取企业及其项目。"""
        service = EnterpriseService()
        created = await service.create(
            db_session, EnterpriseCreate(name="测试企业")
        )

        enterprise = await service.get_with_projects(db_session, created.id)

        assert enterprise is not None
        assert hasattr(enterprise, "projects")

    @pytest.mark.asyncio
    async def test_delete_enterprise_with_projects_blocked(self, db_session):
        """测试有项目的企业不能删除。"""
        from app.services.project import ProjectService
        from app.schemas.project import ProjectCreate

        enterprise_service = EnterpriseService()
        project_service = ProjectService()

        enterprise = await enterprise_service.create(
            db_session, EnterpriseCreate(name="测试企业")
        )
        await project_service.create(
            db_session,
            ProjectCreate(
                name="测试项目",
                enterprise_id=enterprise.id,
                job_title="测试岗位",
            ),
        )

        with pytest.raises(ValueError, match="该企业下存在项目"):
            await enterprise_service.delete(db_session, enterprise.id)
