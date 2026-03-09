"""用户和团队模型。"""

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin
from app.models.enums import UserRole
from app.database import Base


class Team(Base, TimestampMixin):
    """团队表。"""

    __tablename__ = "team"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    manager_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="team", foreign_keys="User.team_id")
    manager: Mapped["User | None"] = relationship("User", foreign_keys=[manager_id], remote_side="User.id", post_update=True)


class User(Base, TimestampMixin):
    """用户表。"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)  # bcrypt hash
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.RECRUITER)
    team_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("team.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    team: Mapped["Team | None"] = relationship("Team", back_populates="users", foreign_keys=[team_id])
    person_projects: Mapped[list["PersonProject"]] = relationship(
        "PersonProject", back_populates="owner", foreign_keys="PersonProject.owner_id"
    )
    follow_ups: Mapped[list["FollowUp"]] = relationship("FollowUp", back_populates="creator")
    reminders: Mapped[list["Reminder"]] = relationship("Reminder", back_populates="creator")


# 避免循环导入
from app.models.person_project import PersonProject
from app.models.follow_up import FollowUp
from app.models.reminder import Reminder
