"""跟进记录 schemas。"""

from datetime import datetime

from pydantic import BaseModel

class FollowUpBase(BaseModel):
    """跟进记录基础模型。"""

    person_project_id: int
    content: str
    next_follow_time: datetime | None = None


class FollowUpCreate(FollowUpBase):
    """创建跟进记录。"""

    pass


class FollowUpResponse(FollowUpBase):
    """跟进记录响应。"""

    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
