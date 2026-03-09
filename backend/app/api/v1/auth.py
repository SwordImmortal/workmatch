"""认证 API 端点。"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.schemas.common import DataResponse
from app.services.auth import AuthService
from app.utils.deps import CurrentUser, DBSession

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=DataResponse[LoginResponse])
async def login(data: LoginRequest, db: DBSession):
    """用户登录。"""
    result = await AuthService.login(db, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    return DataResponse(data=result)


@router.post("/logout")
async def logout():
    """用户登出。"""
    # JWT 是无状态的，客户端删除 token 即可
    return {"message": "登出成功"}


@router.get("/me", response_model=DataResponse[UserResponse])
async def get_current_user_info(current_user: CurrentUser):
    """获取当前用户信息。"""
    return DataResponse(data=UserResponse.model_validate(current_user))
