"""认证服务。"""

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, TokenResponse, UserCreate, UserResponse
from app.utils.security import create_access_token, get_password_hash, verify_password

settings = get_settings()


class AuthService:
    """认证服务。"""

    @staticmethod
    async def authenticate(session: AsyncSession, username: str, password: str) -> User | None:
        """验证用户名和密码。"""
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    async def login(session: AsyncSession, login_data: LoginRequest) -> LoginResponse | None:
        """用户登录。"""
        user = await AuthService.authenticate(
            session, login_data.username, login_data.password
        )
        if not user:
            return None

        # 创建 token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value},
            expires_delta=access_token_expires,
        )

        return LoginResponse(
            user=UserResponse.model_validate(user),
            token=TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
            ),
        )

    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
        """创建用户（仅管理员）。"""
        # 检查用户名是否已存在
        result = await session.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise ValueError("用户名已存在")

        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            password=hashed_password,
            name=user_data.name,
            role=user_data.role,
            team_id=user_data.team_id,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
        """根据 ID 获取用户。"""
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
