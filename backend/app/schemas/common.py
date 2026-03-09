"""通用响应模型。"""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel):
    """基础响应。"""

    code: int = 0
    message: str = "success"
    timestamp: int = 0

    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp == 0:
            self.timestamp = int(datetime.now().timestamp())


class DataResponse(ResponseBase, Generic[T]):
    """数据响应。"""

    data: T


class PaginatedData(BaseModel, Generic[T]):
    """分页数据。"""

    items: list[T]
    total: int
    page: int
    page_size: int


class ListResponse(ResponseBase, Generic[T]):
    """列表响应。"""

    data: list[T]
    total: int
    skip: int = 0
    limit: int = 20


class PaginatedResponse(ResponseBase, Generic[T]):
    """分页响应。"""

    data: PaginatedData[T]


class MessageResponse(ResponseBase):
    """消息响应。"""

    pass
