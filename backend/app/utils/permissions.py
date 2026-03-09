"""权限控制。"""

from functools import wraps

from fastapi import HTTPException, status

from app.models.enums import UserRole
from app.models.user import User


def check_permission(user: User, required_roles: list[UserRole]) -> bool:
    """检查用户是否有权限。"""
    if user.role == UserRole.ADMIN:
        return True  # 管理员拥有所有权限
    return user.role in required_roles


def require_roles(*roles: UserRole):
    """装饰器：要求特定角色。"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: User = None, **kwargs):
            # 从 kwargs 中获取 user
            if user is None:
                for arg in args:
                    if isinstance(arg, User):
                        user = arg
                        break
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证",
                )
            if not check_permission(user, list(roles)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足",
                )
            return await func(*args, user=user, **kwargs)

        return wrapper

    return decorator


# 角色权限矩阵
ROLE_PERMISSIONS = {
    UserRole.ADMIN: ["all"],
    UserRole.MANAGER: ["read", "write", "team_manage"],
    UserRole.RECRUITER: ["read", "write_self"],
}


def can_manage_user(actor: User, target: User) -> bool:
    """检查 actor 是否可以管理 target 用户。"""
    if actor.role == UserRole.ADMIN:
        return True
    if actor.role == UserRole.MANAGER:
        # 主管只能管理自己团队的用户
        return target.team_id == actor.team_id
    return False


def can_access_data(user: User, data_owner_id: int) -> bool:
    """检查用户是否可以访问某数据。"""
    if user.role == UserRole.ADMIN:
        return True
    if user.role == UserRole.MANAGER:
        # 主管可以访问团队数据（需要额外查询）
        return True  # 在服务层进一步验证
    # 专员只能访问自己的数据
    return user.id == data_owner_id
