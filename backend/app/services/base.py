"""基础 CRUD 服务。"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType]):
    """CRUD 基础服务类。"""

    model_class: type[ModelType]

    async def get_by_id(self, session: AsyncSession, id: int) -> ModelType | None:
        """根据 ID 获取。"""
        result = await session.execute(select(self.model_class).where(self.model_class.id == id))
        return result.scalar_one_or_none()

    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100, **filters: Any
    ) -> list[ModelType]:
        """获取列表（分页）。"""
        query = select(self.model_class).offset(skip).limit(limit)
        # 应用过滤条件
        for key, value in filters.items():
            if hasattr(self.model_class, key) and value is not None:
                query = query.where(getattr(self.model_class, key) == value)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, obj_in: Any) -> ModelType:
        """创建记录。"""
        db_obj = self.model_class(**obj_in.model_dump())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self, session: AsyncSession, id: int, obj_in: SchemaType
    ) -> ModelType | None:
        """更新记录。"""
        db_obj = await self.get_by_id(session, id)
        if not db_obj:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, id: int) -> bool:
        """删除记录。"""
        db_obj = await self.get_by_id(session, id)
        if not db_obj:
            return False
        await session.delete(db_obj)
        await session.commit()
        return True
