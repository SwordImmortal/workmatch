"""跟进记录模型。"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class FollowUp(Base, TimestampMixin):
    """跟进记录表。"""

    __tablename__ = "follow_up"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("person_project.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    next_follow_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    # Relationships
    person_project: Mapped["PersonProject"] = relationship("PersonProject", back_populates="follow_ups")
    creator: Mapped["User"] = relationship("User", back_populates="follow_ups")


from app.models.person_project import PersonProject
from app.models.user import User
