"""提醒模型。"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import ReminderStatus


class Reminder(Base, TimestampMixin):
    """提醒表。"""

    __tablename__ = "reminder"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("person_project.id"), nullable=False, index=True
    )
    follow_up_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("follow_up.id"), nullable=True)
    remind_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[ReminderStatus] = mapped_column(
        Enum(ReminderStatus), nullable=False, default=ReminderStatus.PENDING, index=True
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    # Relationships
    person_project: Mapped["PersonProject"] = relationship("PersonProject", back_populates="reminders")
    creator: Mapped["User"] = relationship("User", back_populates="reminders")


from app.models.person_project import PersonProject
from app.models.user import User
