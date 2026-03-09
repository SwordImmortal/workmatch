"""提醒 schemas。"""

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ReminderStatus


class ReminderBase(BaseModel):
    """提醒基础模型。"""

    person_project_id: int
    follow_up_id: int | None = None
    remind_time: datetime
    content: str
    status: ReminderStatus = ReminderStatus.PENDING


    created_by: int


class ReminderCreate(ReminderBase):
    """创建提醒。"""

    pass


class ReminderResponse(ReminderBase):
    """提醒响应。"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReminderUpdate(BaseModel):
    """更新提醒状态。"""

    status: ReminderStatus
