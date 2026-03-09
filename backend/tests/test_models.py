"""模型测试。"""

import pytest
from sqlalchemy import inspect

from app.models import (
    Enterprise,
    FollowUp,
    Person,
    PersonProject,
    Project,
    Reminder,
    StatusHistory,
    Team,
    User,
)
from app.models.enums import (
    FailReason,
    Gender,
    PersonProjectStatus,
    ProjectStatus,
    ReminderStatus,
    Source,
    UserRole,
)


def test_enums_exist():
    """测试枚举定义。"""
    assert UserRole.ADMIN.value == "admin"
    assert UserRole.MANAGER.value == "manager"
    assert UserRole.RECRUITER.value == "recruiter"

    assert PersonProjectStatus.SIGNED_UP.value == "signed_up"
    assert PersonProjectStatus.INVITED.value == "invited"
    assert PersonProjectStatus.FAILED.value == "failed"

    assert FailReason.NO_SHOW.value == "no_show"
    assert FailReason.REJECTED.value == "rejected"


def test_model_tables_exist():
    """测试模型表定义。"""
    # 验证表名
    assert Team.__tablename__ == "team"
    assert User.__tablename__ == "user"
    assert Enterprise.__tablename__ == "enterprise"
    assert Project.__tablename__ == "project"
    assert Person.__tablename__ == "person"
    assert PersonProject.__tablename__ == "person_project"
    assert FollowUp.__tablename__ == "follow_up"
    assert Reminder.__tablename__ == "reminder"
    assert StatusHistory.__tablename__ == "status_history"


def test_model_columns():
    """测试模型列定义。"""
    # User 模型
    user_columns = {col.name for col in inspect(User).columns}
    assert "id" in user_columns
    assert "username" in user_columns
    assert "password" in user_columns
    assert "name" in user_columns
    assert "role" in user_columns
    assert "team_id" in user_columns

    # Person 模型
    person_columns = {col.name for col in inspect(Person).columns}
    assert "id" in person_columns
    assert "name" in person_columns
    assert "phone" in person_columns
    assert "reusable" in person_columns

    # PersonProject 模型（核心）
    pp_columns = {col.name for col in inspect(PersonProject).columns}
    assert "person_id" in pp_columns
    assert "project_id" in pp_columns
    assert "status" in pp_columns
    assert "fail_reason" in pp_columns
    assert "completed_rooms" in pp_columns  # 酒店保洁专用
