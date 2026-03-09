"""人员-项目关联模型（核心）。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import FailReason, PersonProjectStatus


class PersonProject(Base, TimestampMixin):
    """人员项目关联表（核心：一人多项目）。"""

    __tablename__ = "person_project"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("person.id"), nullable=False, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project.id"), nullable=False, index=True)
    status: Mapped[PersonProjectStatus] = mapped_column(
        Enum(PersonProjectStatus), nullable=False, default=PersonProjectStatus.SIGNED_UP, index=True
    )
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # 失败相关
    fail_reason: Mapped[FailReason | None] = mapped_column(Enum(FailReason), nullable=True, index=True)
    fail_remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 京东专用字段
    attended_training: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # 是否到训
    purchased_package: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # 是否购包

    # 酒店保洁专用字段
    completed_rooms: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 已完成间数

    # Relationships
    person: Mapped["Person"] = relationship("Person", back_populates="person_projects")
    project: Mapped["Project"] = relationship("Project", back_populates="person_projects")
    owner: Mapped["User"] = relationship("User", back_populates="person_projects", foreign_keys=[owner_id])
    follow_ups: Mapped[list["FollowUp"]] = relationship("FollowUp", back_populates="person_project")
    reminders: Mapped[list["Reminder"]] = relationship("Reminder", back_populates="person_project")
    status_histories: Mapped[list["StatusHistory"]] = relationship("StatusHistory", back_populates="person_project")

    # 唯一约束：同一人员不能重复分配到同一项目
    __table_args__ = (Index("ix_person_project_unique", "person_id", "project_id", unique=True),)


from app.models.person import Person
from app.models.project import Project
from app.models.user import User
from app.models.follow_up import FollowUp
from app.models.reminder import Reminder
from app.models.status_history import StatusHistory
