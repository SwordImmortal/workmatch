"""PersonProjectService 单元测试。"""

import pytest

from app.models.enums import FailReason, PersonProjectStatus
from app.schemas.enterprise import EnterpriseCreate
from app.schemas.person import PersonCreate
from app.schemas.person_project import PersonProjectCreate, StatusChangeRequest
from app.schemas.project import ProjectCreate
from app.services.enterprise import EnterpriseService
from app.services.person import PersonService
from app.services.person_project import PersonProjectService
from app.services.project import ProjectService


class TestPersonProjectService:
    """PersonProjectService 单元测试。"""

    @pytest.fixture
    async def setup_data(self, db_session):
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

        return {
            "enterprise": enterprise,
            "project": project,
            "person": person,
            "pp_service": pp_service,
            "project_service": project_service,
            "person_service": person_service,
            "enterprise_service": enterprise_service,
        }

    # ==================== 基础 CRUD 测试 ====================

    @pytest.mark.asyncio
    async def test_create_person_project(self, db_session, setup_data):
        """测试创建人员-项目关联。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )

        pp = await data["pp_service"].create(db_session, pp_data)

        assert pp.id is not None
        assert pp.person_id == data["person"].id
        assert pp.project_id == data["project"].id
        assert pp.status == PersonProjectStatus.SIGNED_UP

    @pytest.mark.asyncio
    async def test_create_duplicate_person_project(self, db_session, setup_data):
        """测试创建重复关联抛出异常。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )

        await data["pp_service"].create(db_session, pp_data)

        with pytest.raises(ValueError, match="该人员已分配到此项目"):
            await data["pp_service"].create(db_session, pp_data)

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session, setup_data):
        """测试根据 ID 获取关联。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        created = await data["pp_service"].create(db_session, pp_data)

        pp = await data["pp_service"].get_by_id(db_session, created.id)

        assert pp is not None
        assert pp.id == created.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """测试获取不存在的关联返回 None。"""
        service = PersonProjectService()
        pp = await service.get_by_id(db_session, 999)
        assert pp is None

    # ==================== 状态流转测试 ====================

    @pytest.mark.asyncio
    async def test_advance_status_signed_up_to_invited(self, db_session, setup_data):
        """测试状态流转：已报名 → 已邀约。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        updated = await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.INVITED, changed_by=1
        )

        assert updated.status == PersonProjectStatus.INVITED

    @pytest.mark.asyncio
    async def test_advance_status_invited_to_interview_pending(self, db_session, setup_data):
        """测试状态流转：已邀约 → 待面试。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.INVITED, changed_by=1
        )
        updated = await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.INTERVIEW_PENDING, changed_by=1
        )

        assert updated.status == PersonProjectStatus.INTERVIEW_PENDING

    @pytest.mark.asyncio
    async def test_advance_status_full_flow(self, db_session, setup_data):
        """测试完整状态流转：已报名 → 试工通过。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        # 完整流转
        await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.INVITED, changed_by=1
        )
        await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.INTERVIEW_PENDING, changed_by=1
        )
        await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.INTERVIEWED, changed_by=1
        )
        await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.IN_TRIAL, changed_by=1
        )
        updated = await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.TRIAL_PASSED, changed_by=1
        )

        assert updated.status == PersonProjectStatus.TRIAL_PASSED

    @pytest.mark.asyncio
    async def test_advance_status_skip_forbidden(self, db_session, setup_data):
        """测试非法跳转：已报名 → 待面试（跳过已邀约）应该失败。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        with pytest.raises(ValueError, match="非法状态流转"):
            await data["pp_service"].advance_status(
                db_session, pp.id, PersonProjectStatus.INTERVIEW_PENDING, changed_by=1
            )

    @pytest.mark.asyncio
    async def test_advance_status_jump_to_trial_passed_forbidden(self, db_session, setup_data):
        """测试非法跳转：已报名 → 试工通过 应该失败。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        with pytest.raises(ValueError, match="非法状态流转"):
            await data["pp_service"].advance_status(
                db_session, pp.id, PersonProjectStatus.TRIAL_PASSED, changed_by=1
            )

    # ==================== 失败状态测试 ====================

    @pytest.mark.asyncio
    async def test_advance_status_to_failed_with_reason(self, db_session, setup_data):
        """测试转为失败状态（带原因）。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        updated = await data["pp_service"].advance_status(
            db_session,
            pp.id,
            PersonProjectStatus.FAILED,
            changed_by=1,
            fail_reason=FailReason.REJECTED,
            fail_remark="候选人拒绝",
        )

        assert updated.status == PersonProjectStatus.FAILED
        assert updated.fail_reason == FailReason.REJECTED
        assert updated.fail_remark == "候选人拒绝"

    @pytest.mark.asyncio
    async def test_advance_status_to_failed_without_reason_forbidden(self, db_session, setup_data):
        """测试转为失败状态不带原因应该失败。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        with pytest.raises(ValueError, match="失败状态必须提供失败原因"):
            await data["pp_service"].advance_status(
                db_session, pp.id, PersonProjectStatus.FAILED, changed_by=1
            )

    @pytest.mark.asyncio
    async def test_advance_status_to_unreachable_anytime(self, db_session, setup_data):
        """测试任何状态都可以转为联系不上。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        # 从已报名直接转联系不上
        updated = await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.UNREACHABLE, changed_by=1
        )

        assert updated.status == PersonProjectStatus.UNREACHABLE

    @pytest.mark.asyncio
    async def test_advance_status_to_failed_from_any_status(self, db_session, setup_data):
        """测试任何状态都可以转为失败。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        # 从已报名直接转失败
        updated = await data["pp_service"].advance_status(
            db_session,
            pp.id,
            PersonProjectStatus.FAILED,
            changed_by=1,
            fail_reason=FailReason.OTHER,
        )

        assert updated.status == PersonProjectStatus.FAILED

    # ==================== 状态历史测试 ====================

    @pytest.mark.asyncio
    async def test_status_history_created(self, db_session, setup_data):
        """测试状态变更时创建历史记录。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.INVITED, changed_by=1
        )

        history = await data["pp_service"].get_status_history(db_session, pp.id)

        assert len(history) == 1
        assert history[0].from_status == PersonProjectStatus.SIGNED_UP
        assert history[0].to_status == PersonProjectStatus.INVITED

    @pytest.mark.asyncio
    async def test_status_history_multiple_changes(self, db_session, setup_data):
        """测试多次状态变更的历史记录。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.INVITED, changed_by=1
        )
        await data["pp_service"].advance_status(
            db_session, pp.id, PersonProjectStatus.INTERVIEW_PENDING, changed_by=1
        )

        history = await data["pp_service"].get_status_history(db_session, pp.id)

        assert len(history) == 2
        assert history[0].from_status == PersonProjectStatus.SIGNED_UP
        assert history[0].to_status == PersonProjectStatus.INVITED
        assert history[1].from_status == PersonProjectStatus.INVITED
        assert history[1].to_status == PersonProjectStatus.INTERVIEW_PENDING

    # ==================== 京东专用字段测试 ====================

    @pytest.mark.asyncio
    async def test_update_jd_fields(self, db_session, setup_data):
        """测试更新京东专用字段。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        updated = await data["pp_service"].update(
            db_session,
            pp.id,
            attended_training=True,
            purchased_package=True,
        )

        assert updated.attended_training is True
        assert updated.purchased_package is True

    # ==================== 酒店保洁专用字段测试 ====================

    @pytest.mark.asyncio
    async def test_update_hotel_cleaning_fields(self, db_session, setup_data):
        """测试更新酒店保洁专用字段。"""
        data = setup_data
        pp_data = PersonProjectCreate(
            person_id=data["person"].id,
            project_id=data["project"].id,
            owner_id=1,
        )
        pp = await data["pp_service"].create(db_session, pp_data)

        updated = await data["pp_service"].update(
            db_session,
            pp.id,
            completed_rooms=10,
        )

        assert updated.completed_rooms == 10

    # ==================== 列表查询测试 ====================

    @pytest.mark.asyncio
    async def test_get_list_by_project(self, db_session, setup_data):
        """测试按项目筛选关联列表。"""
        data = setup_data

        # 创建第二个项目和人员
        project2 = await data["project_service"].create(
            db_session,
            ProjectCreate(
                name="项目2",
                enterprise_id=data["enterprise"].id,
                job_title="岗位",
            ),
        )
        person2 = await data["person_service"].create(
            db_session,
            PersonCreate(name="李四", phone="13900139000", city="上海"),
            created_by=1,
        )

        # 创建关联
        await data["pp_service"].create(
            db_session,
            PersonProjectCreate(
                person_id=data["person"].id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )
        await data["pp_service"].create(
            db_session,
            PersonProjectCreate(
                person_id=person2.id,
                project_id=project2.id,
                owner_id=1,
            ),
        )

        pps, total = await data["pp_service"].get_list(
            db_session, project_id=data["project"].id
        )

        assert len(pps) == 1
        assert total == 1
        assert pps[0].project_id == data["project"].id

    @pytest.mark.asyncio
    async def test_get_list_by_status(self, db_session, setup_data):
        """测试按状态筛选关联列表。"""
        data = setup_data

        # 创建关联并推进状态
        pp1 = await data["pp_service"].create(
            db_session,
            PersonProjectCreate(
                person_id=data["person"].id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )
        await data["pp_service"].advance_status(
            db_session, pp1.id, PersonProjectStatus.INVITED, changed_by=1
        )

        # 创建第二个人员
        person2 = await data["person_service"].create(
            db_session,
            PersonCreate(name="李四", phone="13900139000", city="上海"),
            created_by=1,
        )
        await data["pp_service"].create(
            db_session,
            PersonProjectCreate(
                person_id=person2.id,
                project_id=data["project"].id,
                owner_id=1,
            ),
        )

        pps, total = await data["pp_service"].get_list(
            db_session, status=PersonProjectStatus.INVITED
        )

        assert len(pps) == 1
        assert pps[0].status == PersonProjectStatus.INVITED

    # ==================== 统计测试 ====================

    @pytest.mark.asyncio
    async def test_get_project_statistics(self, db_session, setup_data):
        """测试获取项目统计。"""
        data = setup_data

        # 创建多个人员并分配到项目（使用不同手机号避免冲突）
        for i in range(3):
            person = await data["person_service"].create(
                db_session,
                PersonCreate(name=f"人员{i}", phone=f"1390013900{i}", city="北京"),
                created_by=1,
            )
            await data["pp_service"].create(
                db_session,
                PersonProjectCreate(
                    person_id=person.id,
                    project_id=data["project"].id,
                    owner_id=1,
                ),
            )

        stats = await data["pp_service"].get_project_statistics(
            db_session, data["project"].id
        )

        assert stats["total"] == 3
        assert stats["status_breakdown"]["signed_up"] == 3

    # ==================== 异常处理测试 ====================

    @pytest.mark.asyncio
    async def test_advance_status_not_found(self, db_session):
        """测试更新不存在关联的状态返回 None。"""
        service = PersonProjectService()

        result = await service.advance_status(
            db_session, 999, PersonProjectStatus.INVITED, changed_by=1
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_update_not_found(self, db_session):
        """测试更新不存在关联返回 None。"""
        service = PersonProjectService()

        result = await service.update(db_session, 999, completed_rooms=10)

        assert result is None
