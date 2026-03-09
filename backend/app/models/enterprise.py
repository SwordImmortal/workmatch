"""企业模型。"""

from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import EnterpriseStatus


class Enterprise(Base, TimestampMixin):
    """企业表。"""

    __tablename__ = "enterprise"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    contact_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EnterpriseStatus] = mapped_column(
        Enum(EnterpriseStatus), nullable=False, default=EnterpriseStatus.ACTIVE
    )

    # Relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="enterprise")


from app.models.project import Project
