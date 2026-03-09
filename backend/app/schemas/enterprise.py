"""企业 schemas。"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import EnterpriseStatus


class EnterpriseBase(BaseModel):
    """企业基础模型。"""

    name: str = Field(..., max_length=100)
    contact_name: str | None = Field(None, max_length=50)
    contact_phone: str | None = Field(None, max_length=20)
    address: str | None = Field(None, max_length=200)
    description: str | None = None


class EnterpriseCreate(EnterpriseBase):
    """创建企业。"""

    pass


class EnterpriseUpdate(BaseModel):
    """更新企业。"""

    name: str | None = Field(None, max_length=100)
    contact_name: str | None = Field(None, max_length=50)
    contact_phone: str | None = Field(None, max_length=20)
    address: str | None = Field(None, max_length=200)
    description: str | None = None
    status: EnterpriseStatus | None = None


class EnterpriseResponse(EnterpriseBase):
    """企业响应。"""

    id: int
    status: EnterpriseStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
