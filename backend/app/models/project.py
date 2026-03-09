"""项目模型。"""

from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import ProjectStatus


class Project(Base, TimestampMixin):
    """项目表。"""

    __tablename__ = "project"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enterprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprise.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    salary_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    work_address: Mapped[str | None] = mapped_column(String(200), nullable=True)
    requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), nullable=False, default=ProjectStatus.ACTIVE
    )
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)  # 酒店保洁：元/间

    # Relationships
    enterprise: Mapped["Enterprise"] = relationship("Enterprise", back_populates="projects")
    person_projects: Mapped[list["PersonProject"]] = relationship("PersonProject", back_populates="project")
