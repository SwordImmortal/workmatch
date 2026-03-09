"""企业服务。"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.enterprise import Enterprise
from app.models.enums import EnterpriseStatus
from app.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate


class EnterpriseService:
    """企业服务类。"""

    async def create(
        self, session: AsyncSession, enterprise_data: EnterpriseCreate
    ) -> Enterprise:
        """创建企业。"""
        # 检查企业名称是否已存在
        existing = await session.execute(
            select(Enterprise).where(Enterprise.name == enterprise_data.name)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"企业名称已存在: {enterprise_data.name}")

        enterprise = Enterprise(
            name=enterprise_data.name,
            contact_name=enterprise_data.contact_name,
            contact_phone=enterprise_data.contact_phone,
            address=enterprise_data.address,
            description=enterprise_data.description,
        )
        session.add(enterprise)
        await session.commit()
        await session.refresh(enterprise)
        return enterprise

    async def get_by_id(self, session: AsyncSession, enterprise_id: int) -> Enterprise | None:
        """根据 ID 获取企业。"""
        result = await session.execute(
            select(Enterprise).where(Enterprise.id == enterprise_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: EnterpriseStatus | None = None,
        search: str | None = None,
    ) -> tuple[list[Enterprise], int]:
        """获取企业列表。"""
        query = select(Enterprise)

        # 筛选条件
        if status:
            query = query.where(Enterprise.status == status)
        if search:
            escaped_search = search.replace("%", r"\%").replace("_", r"\_")
            search_pattern = f"%{escaped_search}%"
            query = query.where(Enterprise.name.ilike(search_pattern, escape="\\"))

        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(Enterprise.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        enterprises = list(result.scalars().all())

        return enterprises, total

    async def update(
        self, session: AsyncSession, enterprise_id: int, enterprise_data: EnterpriseUpdate
    ) -> Enterprise | None:
        """更新企业信息。"""
        enterprise = await self.get_by_id(session, enterprise_id)
        if not enterprise:
            return None

        update_dict = enterprise_data.model_dump(exclude_unset=True)

        # 检查企业名称唯一性（如果要更新名称）
        if "name" in update_dict and update_dict["name"] != enterprise.name:
            existing = await session.execute(
                select(Enterprise).where(Enterprise.name == update_dict["name"])
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"企业名称已存在: {update_dict['name']}")

        # ORM 层变更追踪
        for field, value in update_dict.items():
            setattr(enterprise, field, value)

        await session.commit()
        await session.refresh(enterprise)
        return enterprise

    async def delete(self, session: AsyncSession, enterprise_id: int) -> bool:
        """删除企业。"""
        enterprise = await self.get_by_id(session, enterprise_id)
        if not enterprise:
            return False

        # 检查是否有关联项目
        from app.models.project import Project

        projects = await session.execute(
            select(Project).where(Project.enterprise_id == enterprise_id).limit(1)
        )
        if projects.scalar_one_or_none():
            raise ValueError("该企业下存在项目，无法删除")

        await session.delete(enterprise)
        await session.commit()
        return True

    async def get_with_projects(self, session: AsyncSession, enterprise_id: int) -> Enterprise | None:
        """获取企业及其项目列表。"""
        result = await session.execute(
            select(Enterprise)
            .options(joinedload(Enterprise.projects))
            .where(Enterprise.id == enterprise_id)
        )
        return result.unique().scalar_one_or_none()
