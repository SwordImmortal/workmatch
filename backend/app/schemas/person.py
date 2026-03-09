"""人员 schemas。"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import Gender, Source


class PersonBase(BaseModel):
    """人员基础模型。"""

    name: str = Field(..., max_length=50)
    phone: str = Field(..., max_length=20)
    id_card: str | None = Field(None, max_length=18)
    gender: Gender = Gender.UNKNOWN
    age: int | None = Field(None, ge=0, le=150)
    city: str = Field(..., max_length=50)
    address: str | None = Field(None, max_length=200)
    source: Source = Source.OTHER
    remark: str | None = None
    reusable: bool = True


class PersonCreate(PersonBase):
    """创建人员。"""

    pass


class PersonUpdate(BaseModel):
    """更新人员。"""

    name: str | None = Field(None, max_length=50)
    phone: str | None = Field(None, max_length=20)
    id_card: str | None = Field(None, max_length=18)
    gender: Gender | None = None
    age: int | None = Field(None, ge=0, le=150)
    city: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=200)
    source: Source | None = None
    remark: str | None = None
    reusable: bool | None = None


class PersonResponse(PersonBase):
    """人员响应。"""

    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PersonWithProjectsResponse(PersonResponse):
    """人员响应（含项目列表）。"""

    projects: list["PersonProjectSummary"]


class PersonProjectSummary(BaseModel):
    """人员项目摘要。"""

    project_id: int
    project_name: str
    status: str
    owner_name: str

    model_config = {"from_attributes": True}


# 避免循环导入
PersonWithProjectsResponse.model_rebuild()
