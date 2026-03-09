"""企业 API 端点。"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, validate_pagination
from app.schemas.common import DataResponse, ListResponse
from app.schemas.enterprise import EnterpriseCreate, EnterpriseResponse, EnterpriseUpdate
from app.services.enterprise import EnterpriseService
from app.utils.deps import CurrentUser, DBSession

router = APIRouter(prefix="/enterprises", tags=["企业管理"])
enterprise_service = EnterpriseService()


@router.post("/", response_model=DataResponse[EnterpriseResponse], status_code=status.HTTP_201_CREATED)
async def create_enterprise(
    data: EnterpriseCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """创建企业。"""
    try:
        enterprise = await enterprise_service.create(db, data)
        return DataResponse(data=EnterpriseResponse.model_validate(enterprise))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=ListResponse[EnterpriseResponse])
async def list_enterprises(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
    name: str | None = Query(None, description="企业名称搜索"),
    status_filter: str | None = Query(None, alias="status", description="状态筛选"),
):
    """获取企业列表。"""
    skip, limit = validate_pagination(skip, limit)
    enterprises, total = await enterprise_service.get_list(
        db,
        skip=skip,
        limit=limit,
        name=name,
        status=status_filter,
    )
    return ListResponse(
        data=[EnterpriseResponse.model_validate(e) for e in enterprises],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{enterprise_id}", response_model=DataResponse[EnterpriseResponse])
async def get_enterprise(
    enterprise_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """获取企业详情。"""
    enterprise = await enterprise_service.get_by_id(db, enterprise_id)
    if not enterprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="企业不存在",
        )
    return DataResponse(data=EnterpriseResponse.model_validate(enterprise))


@router.put("/{enterprise_id}", response_model=DataResponse[EnterpriseResponse])
async def update_enterprise(
    enterprise_id: int,
    data: EnterpriseUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """更新企业信息。"""
    try:
        enterprise = await enterprise_service.update(db, enterprise_id, data)
        if not enterprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="企业不存在",
            )
        return DataResponse(data=EnterpriseResponse.model_validate(enterprise))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{enterprise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enterprise(
    enterprise_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """删除企业。"""
    success = await enterprise_service.delete(db, enterprise_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="企业不存在",
        )
