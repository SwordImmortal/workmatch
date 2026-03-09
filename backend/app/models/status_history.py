"""状态变更历史模型。"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import PersonProjectStatus


class StatusHistory(Base, TimestampMixin):
    """状态变更历史表。"""

    __tablename__ = "status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("person_project.id"), nullable=False, index=True
    )
    from_status: Mapped[PersonProjectStatus | None] = mapped_column(Enum(PersonProjectStatus), nullable=True)
    to_status: Mapped[PersonProjectStatus] = mapped_column(Enum(PersonProjectStatus), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    changed_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    # Relationships
    person_project: Mapped["PersonProject"] = relationship("PersonProject", back_populates="status_histories")

    # 复合索引：用于按项目统计
    __table_args__ = (Index("ix_status_history_project_time", "person_project_id", "changed_at"),)


from app.models.person_project import PersonProject
