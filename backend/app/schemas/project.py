"""项目 schemas。"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import ProjectStatus


class ProjectBase(BaseModel):
    """项目基础模型。"""

    enterprise_id: int
    name: str = Field(..., max_length=100)
    job_title: str = Field(..., max_length=100)
    salary_range: str | None = Field(None, max_length=50)
    work_address: str | None = Field(None, max_length=200)
    requirement: str | None = None
    priority: int = 0
    unit_price: Decimal | None = None


class ProjectCreate(ProjectBase):
    """创建项目。"""

    pass


class ProjectUpdate(BaseModel):
    """更新项目。"""

    enterprise_id: int | None = None
    name: str | None = Field(None, max_length=100)
    job_title: str | None = Field(None, max_length=100)
    salary_range: str | None = Field(None, max_length=50)
    work_address: str | None = Field(None, max_length=200)
    requirement: str | None = None
    priority: int | None = None
    status: ProjectStatus | None = None
    unit_price: Decimal | None = None


class ProjectResponse(ProjectBase):
    """项目响应。"""

    id: int
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectWithEnterpriseResponse(ProjectResponse):
    """项目响应（含企业信息）。"""

    enterprise_name: str


class ProjectStatistics(BaseModel):
    """项目统计数据。"""

    project_id: int
    project_name: str
    total: int
    signed_up: int
    invited: int
    interview_pending: int
    interviewed: int
    in_trial: int
    trial_passed: int
    failed: int
    unreachable: int
    failed_breakdown: dict[str, int]
    conversion_rates: dict[str, float]
