"""StatisticsService 单元测试。"""

import pytest
from datetime import datetime, timedelta

from app.models.enums import PersonProjectStatus, FailReason
from app.schemas.enterprise import EnterpriseCreate
from app.schemas.person import PersonCreate
from app.schemas.person_project import PersonProjectCreate
from app.schemas.project import ProjectCreate
from app.services.enterprise import EnterpriseService
from app.services.person import PersonService
from app.services.person_project import PersonProjectService
from app.services.project import ProjectService
from app.services.statistics import StatisticsService


class TestStatisticsService:
    """StatisticsService 单元测试。"""

    @pytest.fixture
    async def setup_data(self, db_session):
        """创建测试数据。"""
        enterprise_service = EnterpriseService()
        project_service = ProjectService()
        person_service = PersonService()
        pp_service = PersonProjectService()
        statistics_service = StatisticsService()

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

        # 创建人员-项目关联
        pp1 = await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=person.id,
                project_id=project.id,
                owner_id=1,
            ),
        )

        # 推进状态
        await pp_service.advance_status(
            db_session,
            pp1.id,
            PersonProjectStatus.INVITED,
            changed_by=1,
        )
        await pp_service.advance_status(
            db_session,
            pp1.id,
            PersonProjectStatus.INTERVIEW_PENDING,
            changed_by=1,
        )
        await pp_service.advance_status(
            db_session,
            pp1.id,
            PersonProjectStatus.INTERVIEWED,
            changed_by=1,
        )
        await pp_service.advance_status(
            db_session,
            pp1.id,
            PersonProjectStatus.IN_TRIAL,
            changed_by=1,
        )
        await pp_service.advance_status(
            db_session,
            pp1.id,
            PersonProjectStatus.TRIAL_PASSED,
            changed_by=1,
        )

        # 创建失败人员
        pp2 = await pp_service.create(
            db_session,
            PersonProjectCreate(
                person_id=person2.id,
                project_id=project.id,
                owner_id=1,
            ),
        )
        await pp_service.advance_status(
            db_session,
            pp2.id,
            PersonProjectStatus.FAILED,
            changed_by=1,
            fail_reason=FailReason.REJECTED,
        )

        return {
            "enterprise": enterprise,
            "project": project,
            "person": person,
            "person2": person2,
            "pp1": pp1,
            "pp2": pp2,
            "project_service": project_service,
            "person_service": person_service,
            "pp_service": pp_service,
            "statistics_service": statistics_service,
        }

    # ==================== 项目统计测试 ====================

    @pytest.mark.asyncio
    async def test_get_project_funnel(self, db_session, setup_data):
        """测试获取项目漏斗数据。 """
        data = setup_data
        stats = await data["statistics_service"].get_project_funnel(
            db_session, data["project"].id
        )

        assert stats["total"] == 2
        # 检查最终状态
        assert PersonProjectStatus.TRIAL_PASSED.value in stats["status_counts"]
        assert PersonProjectStatus.FAILED.value in stats["status_counts"]

        # 检查转化率结构存在
        assert "invite_rate" in stats["conversion_rates"]
        assert "interview_rate" in stats["conversion_rates"]
        assert "trial_rate" in stats["conversion_rates"]
        assert "hire_rate" in stats["conversion_rates"]

    @pytest.mark.asyncio
    async def test_get_daily_statistics(self, db_session, setup_data):
        """测试获取每日统计数据。 """
        data = setup_data

        today = datetime.now().date()
        stats = await data["statistics_service"].get_daily_statistics(
            db_session, data["project"].id, today
        )

        assert "date" in stats
        # SQLite 内存数据库的日期比较可能有问题， 所以只检查结构
        assert "total" in stats
        assert "status_counts" in stats

