"""人员-项目关联 API 端点。"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, validate_pagination
from app.schemas.common import DataResponse, ListResponse, MessageResponse
from app.schemas.person_project import (
    PersonProjectCreate,
    PersonProjectResponse,
    ReassignRequest,
    ReassignResponse,
    StatusAdvanceRequest,
)
from app.services.person_project import PersonProjectService
from app.utils.deps import CurrentUser, DBSession

router = APIRouter(prefix="/person-projects", tags=["人员-项目关联"])
pp_service = PersonProjectService()


@router.post("/", response_model=DataResponse[PersonProjectResponse], status_code=status.HTTP_201_CREATED)
async def create_person_project(
    data: PersonProjectCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """创建人员-项目关联（分配人员到项目）。"""
    try:
        pp = await pp_service.create(db, data)
        return DataResponse(data=PersonProjectResponse.model_validate(pp))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/project/{project_id}", response_model=ListResponse[PersonProjectResponse])
async def list_by_project(
    project_id: int,
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
    status_filter: str | None = Query(None, alias="status", description="状态筛选"),
):
    """获取项目下的人员列表。"""
    skip, limit = validate_pagination(skip, limit)
    items = await pp_service.get_by_project(
        db,
        project_id,
        status=status_filter,
    )
    # 分页处理
    total = len(items)
    paginated_items = items[skip : skip + limit]
    return ListResponse(
        data=[PersonProjectResponse.model_validate(pp) for pp in paginated_items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/person/{person_id}", response_model=ListResponse[PersonProjectResponse])
async def list_by_person(
    person_id: int,
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
):
    """获取人员的项目列表。"""
    skip, limit = validate_pagination(skip, limit)
    items = await pp_service.get_by_person(db, person_id)
    total = len(items)
    paginated_items = items[skip : skip + limit]
    return ListResponse(
        data=[PersonProjectResponse.model_validate(pp) for pp in paginated_items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{pp_id}", response_model=DataResponse[PersonProjectResponse])
async def get_person_project(
    pp_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """获取人员-项目关联详情。"""
    pp = await pp_service.get_by_id(db, pp_id)
    if not pp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联不存在",
        )
    return DataResponse(data=PersonProjectResponse.model_validate(pp))


@router.post("/{pp_id}/status", response_model=DataResponse[PersonProjectResponse])
async def change_status(
    pp_id: int,
    data: StatusAdvanceRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """变更人员项目状态。"""
    try:
        pp = await pp_service.advance_status(
            db,
            pp_id,
            data.status,
            changed_by=current_user.id,
            fail_reason=data.fail_reason,
        )
        if not pp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联不存在",
            )
        return DataResponse(data=PersonProjectResponse.model_validate(pp))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{pp_id}/reassign", response_model=DataResponse[ReassignResponse])
async def reassign_person(
    pp_id: int,
    data: ReassignRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """人力池再分配（将失败人员分配到新项目）。"""
    try:
        pp = await pp_service.reassign(
            db,
            pp_id,
            data.project_id,
            data.owner_id,
        )
        if not pp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联不存在",
            )
        return DataResponse(
            data=ReassignResponse(
                person_project_id=pp.id,
                person_id=pp.person_id,
                project_id=pp.project_id,
                status=pp.status,
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{pp_id}", response_model=MessageResponse)
async def delete_person_project(
    pp_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """删除人员-项目关联。"""
    success = await pp_service.delete(db, pp_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联不存在",
        )
    return MessageResponse(message="删除成功")
