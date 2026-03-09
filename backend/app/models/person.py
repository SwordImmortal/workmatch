"""人员模型。"""

from sqlalchemy import Boolean, Enum, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import Gender, Source


class Person(Base, TimestampMixin):
    """人员表（候选人）。"""

    __tablename__ = "person"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    id_card: Mapped[str | None] = mapped_column(String(18), nullable=True)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False, default=Gender.UNKNOWN)
    age: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source: Mapped[Source] = mapped_column(Enum(Source), nullable=False, default=Source.OTHER, index=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    reusable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # 是否可复用（人力池）
    created_by: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    person_projects: Mapped[list["PersonProject"]] = relationship("PersonProject", back_populates="person")


from app.models.person_project import PersonProject
