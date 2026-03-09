"""人员-项目关联 schemas。"""

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import FailReason, PersonProjectStatus


class PersonProjectBase(BaseModel):
    """人员项目关联基础模型。"""

    person_id: int
    project_id: int
    owner_id: int


class PersonProjectCreate(PersonProjectBase):
    """创建人员项目关联（分配人员到项目）。"""

    pass


class StatusChangeRequest(BaseModel):
    """状态变更请求。"""

    status: PersonProjectStatus
    fail_reason: FailReason | None = None
    fail_remark: str | None = None


# 兼容旧字段名
StatusAdvanceRequest = StatusChangeRequest


class PersonProjectResponse(PersonProjectBase):
    """人员项目关联响应。"""

    id: int
    status: PersonProjectStatus
    fail_reason: FailReason | None
    fail_remark: str | None
    attended_training: bool | None
    purchased_package: bool | None
    completed_rooms: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PersonProjectDetailResponse(PersonProjectResponse):
    """人员项目关联详情响应。"""

    person_name: str
    person_phone: str
    project_name: str
    enterprise_name: str
    owner_name: str


class ReassignRequest(BaseModel):
    """人力池再分配请求。"""

    project_id: int
    owner_id: int


class ReassignResponse(BaseModel):
    """人力池再分配响应。"""

    person_project_id: int
    person_id: int
    project_id: int
    status: PersonProjectStatus
