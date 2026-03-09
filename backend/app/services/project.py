"""项目服务。"""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.enterprise import Enterprise
from app.models.project import Project
from app.models.enums import ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """项目服务类。"""

    async def create(
        self, session: AsyncSession, project_data: ProjectCreate
    ) -> Project:
        """创建项目。"""
        # 验证企业存在
        enterprise = await session.execute(
            select(Enterprise).where(Enterprise.id == project_data.enterprise_id)
        )
        if not enterprise.scalar_one_or_none():
            raise ValueError(f"企业不存在: {project_data.enterprise_id}")

        project = Project(
            enterprise_id=project_data.enterprise_id,
            name=project_data.name,
            job_title=project_data.job_title,
            salary_range=project_data.salary_range,
            work_address=project_data.work_address,
            requirement=project_data.requirement,
            priority=project_data.priority,
            unit_price=Decimal(str(project_data.unit_price)) if project_data.unit_price else None,
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

    async def get_by_id(self, session: AsyncSession, project_id: int) -> Project | None:
        """根据 ID 获取项目。"""
        result = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        enterprise_id: int | None = None,
        status: ProjectStatus | None = None,
        search: str | None = None,
    ) -> tuple[list[Project], int]:
        """获取项目列表。"""
        query = select(Project)

        # 筛选条件
        if enterprise_id:
            query = query.where(Project.enterprise_id == enterprise_id)
        if status:
            query = query.where(Project.status == status)
        if search:
            escaped_search = search.replace("%", r"\%").replace("_", r"\_")
            search_pattern = f"%{escaped_search}%"
            query = query.where(
                Project.name.ilike(search_pattern, escape="\\")
            )

        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(Project.priority.desc(), Project.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        projects = list(result.scalars().all())

        return projects, total

    async def update(
        self, session: AsyncSession, project_id: int, project_data: ProjectUpdate
    ) -> Project | None:
        """更新项目信息。"""
        project = await self.get_by_id(session, project_id)
        if not project:
            return None

        update_dict = project_data.model_dump(exclude_unset=True)

        # 处理 unit_price 转换
        if "unit_price" in update_dict and update_dict["unit_price"] is not None:
            update_dict["unit_price"] = Decimal(str(update_dict["unit_price"]))

        # ORM 层变更追踪
        for field, value in update_dict.items():
            setattr(project, field, value)

        await session.commit()
        await session.refresh(project)
        return project

    async def delete(self, session: AsyncSession, project_id: int) -> bool:
        """删除项目。"""
        project = await self.get_by_id(session, project_id)
        if not project:
            return False

        # 检查是否有关联人员
        from app.models.person_project import PersonProject

        persons = await session.execute(
            select(PersonProject).where(PersonProject.project_id == project_id).limit(1)
        )
        if persons.scalar_one_or_none():
            raise ValueError("该项目下存在人员，无法删除")

        await session.delete(project)
        await session.commit()
        return True

    async def get_with_enterprise(self, session: AsyncSession, project_id: int) -> Project | None:
        """获取项目及其所属企业。"""
        result = await session.execute(
            select(Project)
            .options(joinedload(Project.enterprise))
            .where(Project.id == project_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_statistics(self, session: AsyncSession, project_id: int) -> dict | None:
        """获取项目统计数据。"""
        project = await self.get_by_id(session, project_id)
        if not project:
            return None

        from app.models.person_project import PersonProject
        from sqlalchemy import case

        # 统计各状态人数
        result = await session.execute(
            select(
                func.count().label("total"),
                func.sum(
                    case((PersonProject.status == "signed_up", 1), else_=0)
                ).label("signed_up"),
                func.sum(
                    case((PersonProject.status == "interview_pending", 1), else_=0)
                ).label("interview_pending"),
                func.sum(
                    case((PersonProject.status == "interviewed", 1), else_=0)
                ).label("interviewed"),
                func.sum(
                    case((PersonProject.status == "in_trial", 1), else_=0)
                ).label("in_trial"),
                func.sum(
                    case((PersonProject.status == "trial_passed", 1), else_=0)
                ).label("trial_passed"),
                func.sum(
                    case((PersonProject.status == "failed", 1), else_=0)
                ).label("failed"),
            ).where(PersonProject.project_id == project_id)
        )
        row = result.one()

        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_persons": row.total or 0,
            "status_breakdown": {
                "signed_up": row.signed_up or 0,
                "interview_pending": row.interview_pending or 0,
                "interviewed": row.interviewed or 0,
                "in_trial": row.in_trial or 0,
                "trial_passed": row.trial_passed or 0,
                "failed": row.failed or 0,
            },
        }
