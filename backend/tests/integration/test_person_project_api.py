"""人员-项目关联服务集成测试。"""

import pytest
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Enterprise, Project, Person, PersonProject
from app.models.enums import UserRole, PersonProjectStatus, FailReason
from app.schemas.person import PersonCreate
from app.schemas.enterprise import EnterpriseCreate
from app.schemas.project import ProjectCreate
from app.schemas.person_project import PersonProjectCreate
from app.services.enterprise import EnterpriseService
from app.services.person import PersonService
from app.services.project import ProjectService
from app.services.person_project import PersonProjectService
from app.utils.security import get_password_hash, create_access_token


from tests.integration.conftest import db_session


@pytest.fixture
async def local_setup_data(db_session: AsyncSession):
    """创建测试数据。"""
    enterprise_service = EnterpriseService()
    project_service = ProjectService()
    person_service = PersonService()
    pp_service = PersonProjectService()

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

    # 创建第二个人员
    person2 = await person_service.create(
        db_session,
        PersonCreate(name="李四", phone="13900139000", city="上海"),
        created_by=1,
    )

    return {
        "enterprise": enterprise,
        "project": project,
        "person": person,
        "person2": person2,
        "pp_service": pp_service,
    }


class TestPersonProjectIntegration:
    """人员-项目关联集成测试。"""

    @pytest.mark.asyncio
    async def test_create_person_project(self, db_session, local_setup_data):
        """测试创建人员-项目关联。"""
        data = local_setup_data
        pp_service = data["pp_service"]

        pp = await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=data["person"].id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )

        assert pp.id is not None
        assert pp.person_id == data["person"].id
        assert pp.project_id == data["project"].id
        assert pp.status == PersonProjectStatus.SIGNED_UP

    @pytest.mark.asyncio
    async def test_create_duplicate_person_project(
        self, db_session, local_setup_data
    ):
        """测试创建重复关联应失败。"""
        data = local_setup_data
        pp_service = data["pp_service"]

        # 先创建一个关联
        await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=data["person"].id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )

        # 尝试再次创建应抛出异常
        with pytest.raises(Exception):  # 应该是 IntegrityError 或自定义异常
            await pp_service.create(
                db_session,
                PersonProjectCreate(
                    person_id=data["person"].id,
                    project_id=data["project"].id,
                    owner_id=1,
                ),
            )

    @pytest.mark.asyncio
    async def test_status_transition_flow(self, db_session, local_setup_data):
        """测试完整状态流转。"""
        data = local_setup_data
        pp_service = data["pp_service"]

        # 创建关联
        pp = await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=data["person"].id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )
        assert pp.status == PersonProjectStatus.SIGNED_UP

        # 已报名 -> 已邀约
        pp = await pp_service.advance_status(
            db_session, pp.id, PersonProjectStatus.INVITED, changed_by=1
        )
        assert pp.status == PersonProjectStatus.INVITED

        # 已邀约 -> 待面试
        pp = await pp_service.advance_status(
            db_session, pp.id, PersonProjectStatus.INTERVIEW_PENDING, changed_by=1
        )
        assert pp.status == PersonProjectStatus.INTERVIEW_PENDING

        # 待面试 -> 已面试
        pp = await pp_service.advance_status(
            db_session, pp.id, PersonProjectStatus.INTERVIEWED, changed_by=1
        )
        assert pp.status == PersonProjectStatus.INTERVIEWED

        # 已面试 -> 试工中
        pp = await pp_service.advance_status(
            db_session, pp.id, PersonProjectStatus.IN_TRIAL, changed_by=1
        )
        assert pp.status == PersonProjectStatus.IN_TRIAL

        # 试工中 -> 试工通过
        pp = await pp_service.advance_status(
            db_session, pp.id, PersonProjectStatus.TRIAL_PASSED, changed_by=1
        )
        assert pp.status == PersonProjectStatus.TRIAL_PASSED

    @pytest.mark.asyncio
    async def test_invalid_status_transition(self, db_session, local_setup_data):
        """测试非法状态流转应失败。"""
        data = local_setup_data
        pp_service = data["pp_service"]

        # 创建关联（初始状态：已报名)
        pp = await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=data["person"].id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )

        # 尝试直接跳到试工通过(非法流转)
        with pytest.raises(ValueError, match="非法状态流转"):
            await pp_service.advance_status(
                db_session, pp.id, PersonProjectStatus.TRIAL_PASSED, changed_by=1
            )

    @pytest.mark.asyncio
    async def test_mark_failed_with_reason(self, db_session, local_setup_data):
        """测试标记失败(带原因)。"""
        data = local_setup_data
        pp_service = data["pp_service"]

        # 创建关联
        pp = await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=data["person"].id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )

        # 标记失败
        pp = await pp_service.advance_status(
            db_session,
            pp.id,
            PersonProjectStatus.FAILED,
            changed_by=1,
            fail_reason=FailReason.REJECTED,
        )

        assert pp.status == PersonProjectStatus.FAILED
        assert pp.fail_reason == FailReason.REJECTED

    @pytest.mark.asyncio
    async def test_mark_failed_without_reason_fails(
        self, db_session, local_setup_data
    ):
        """测试标记失败不带原因应失败。"""
        data = local_setup_data
        pp_service = data["pp_service"]

        # 创建关联
        pp = await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=data["person"].id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )

        # 尝试标记失败不带原因
        with pytest.raises(ValueError, match="必须提供失败原因"):
            await pp_service.advance_status(
                db_session, pp.id, PersonProjectStatus.FAILED, changed_by=1
            )

    @pytest.mark.asyncio
    async def test_mark_unreachable(self, db_session, local_setup_data):
        """测试标记联系不上。"""
        data = local_setup_data
        pp_service = data["pp_service"]

        # 创建关联
        pp = await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=data["person"].id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )

        # 从已报名直接标记联系不上
        pp = await pp_service.advance_status(
            db_session, pp.id, PersonProjectStatus.UNREACHABLE, changed_by=1
        )

        assert pp.status == PersonProjectStatus.UNREACHABLE
