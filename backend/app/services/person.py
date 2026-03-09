"""人员服务。"""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.person import Person
from app.models.user import User
from app.schemas.person import PersonCreate, PersonUpdate
from app.utils.permissions import can_access_data


class PersonService:
    """人员服务类。"""

    async def create(
        self, session: AsyncSession, person_data: PersonCreate, created_by: int
    ) -> Person:
        """创建人员。"""
        # 检查手机号是否已存在
        existing = await session.execute(
            select(Person).where(Person.phone == person_data.phone)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"手机号已存在: {person_data.phone}")

        person = Person(
            name=person_data.name,
            phone=person_data.phone,
            id_card=person_data.id_card,
            gender=person_data.gender,
            age=person_data.age,
            city=person_data.city,
            address=person_data.address,
            source=person_data.source,
            remark=person_data.remark,
            reusable=person_data.reusable,
            created_by=created_by,
        )
        session.add(person)
        await session.commit()
        await session.refresh(person)
        return person

    async def get_by_id(
        self, session: AsyncSession, person_id: int, user: User | None = None
    ) -> Person | None:
        """根据 ID 获取人员。"""
        result = await session.execute(select(Person).where(Person.id == person_id))
        person = result.scalar_one_or_none()

        # 权限验证：如果提供了用户，检查是否有权访问
        if person and user:
            if not can_access_data(user, person.created_by):
                return None  # 返回 None 而非抛出异常，避免信息泄露

        return person

    async def get_list(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        city: str | None = None,
        source: str | None = None,
        reusable: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[Person], int]:
        """获取人员列表。"""
        query = select(Person)

        # 筛选条件
        if city:
            query = query.where(Person.city == city)
        if source:
            query = query.where(Person.source == source)
        if reusable is not None:
            query = query.where(Person.reusable == reusable)
        if search:
            # 转义 LIKE 通配符，防止意外匹配
            escaped_search = search.replace("%", r"\%").replace("_", r"\_")
            search_pattern = f"%{escaped_search}%"
            query = query.where(
                or_(
                    Person.name.ilike(search_pattern, escape="\\"),
                    Person.phone.ilike(search_pattern, escape="\\"),
                )
            )

        # 统计总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(Person.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        persons = list(result.scalars().all())

        return persons, total

    async def update(
        self,
        session: AsyncSession,
        person_id: int,
        person_data: PersonUpdate,
        user: User | None = None,
    ) -> Person | None:
        """更新人员信息。"""
        person = await self.get_by_id(session, person_id, user)
        if not person:
            return None

        update_dict = person_data.model_dump(exclude_unset=True)

        # 检查手机号唯一性（如果要更新手机号）
        if "phone" in update_dict and update_dict["phone"] != person.phone:
            existing = await session.execute(
                select(Person).where(Person.phone == update_dict["phone"])
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"手机号已存在: {update_dict['phone']}")

        # ORM 层变更追踪：直接设置属性
        for field, value in update_dict.items():
            setattr(person, field, value)

        await session.commit()
        await session.refresh(person)
        return person

    async def delete(
        self, session: AsyncSession, person_id: int, user: User | None = None
    ) -> bool:
        """删除人员。"""
        person = await self.get_by_id(session, person_id, user)
        if not person:
            return False

        await session.delete(person)
        await session.commit()
        return True

    async def get_with_projects(self, session: AsyncSession, person_id: int) -> Person | None:
        """获取人员及其项目状态。"""
        result = await session.execute(
            select(Person)
            .options(joinedload(Person.person_projects))
            .where(Person.id == person_id)
        )
        return result.unique().scalar_one_or_none()
