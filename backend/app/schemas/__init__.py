"""Pydantic schemas 导出。"""

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.schemas.common import DataResponse, MessageResponse, PaginatedData, PaginatedResponse, ResponseBase
from app.schemas.enterprise import EnterpriseCreate, EnterpriseResponse, EnterpriseUpdate
from app.schemas.follow_up import FollowUpCreate, FollowUpResponse
from app.schemas.person import PersonCreate, PersonResponse, PersonUpdate, PersonWithProjectsResponse
from app.schemas.person_project import (
    PersonProjectCreate,
    PersonProjectDetailResponse,
    PersonProjectResponse,
    ReassignRequest,
    ReassignResponse,
    StatusChangeRequest,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatistics,
    ProjectUpdate,
    ProjectWithEnterpriseResponse,
)
from app.schemas.reminder import ReminderCreate, ReminderResponse, ReminderUpdate

__all__ = [
    # Common
    "ResponseBase",
    "DataResponse",
    "MessageResponse",
    "PaginatedData",
    "PaginatedResponse",
    # Auth
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    # Person
    "PersonCreate",
    "PersonUpdate",
    "PersonResponse",
    "PersonWithProjectsResponse",
    # Enterprise
    "EnterpriseCreate",
    "EnterpriseUpdate",
    "EnterpriseResponse",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectWithEnterpriseResponse",
    "ProjectStatistics",
    # PersonProject
    "PersonProjectCreate",
    "PersonProjectResponse",
    "PersonProjectDetailResponse",
    "StatusChangeRequest",
    "ReassignRequest",
    "ReassignResponse",
    # FollowUp
    "FollowUpCreate",
    "FollowUpResponse",
    # Reminder
    "ReminderCreate",
    "ReminderResponse",
    "ReminderUpdate",
]
