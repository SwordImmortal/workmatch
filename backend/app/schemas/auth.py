"""用户认证 schemas。"""

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import UserRole


class UserBase(BaseModel):
    """用户基础模型。"""

    username: str
    name: str
    role: UserRole = UserRole.RECRUITER
    team_id: int | None = None


class UserCreate(UserBase):
    """创建用户。"""

    password: str


class UserUpdate(BaseModel):
    """更新用户。"""

    name: str | None = None
    role: UserRole | None = None
    team_id: int | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """用户响应。"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """登录请求。"""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Token 响应。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    """登录响应。"""

    user: UserResponse
    token: TokenResponse
