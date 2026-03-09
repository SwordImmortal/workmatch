"""跟进记录 API 端点。"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, validate_pagination
from app.schemas.common import DataResponse, ListResponse, MessageResponse
from app.schemas.follow_up import FollowUpCreate, FollowUpResponse
from app.services.follow_up import FollowUpService
from app.utils.deps import CurrentUser, DBSession

router = APIRouter(prefix="/follow-ups", tags=["跟进记录"])
follow_up_service = FollowUpService()


@router.post("/", response_model=DataResponse[FollowUpResponse], status_code=status.HTTP_201_CREATED)
async def create_follow_up(
    data: FollowUpCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """添加跟进记录。"""
    follow_up = await follow_up_service.create(
        db,
        data,
        created_by=current_user.id,
    )
    return DataResponse(data=FollowUpResponse.model_validate(follow_up))


@router.get("/person/{person_id}", response_model=ListResponse[FollowUpResponse])
async def list_by_person(
    person_id: int,
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
):
    """获取人员的跟进记录列表。"""
    skip, limit = validate_pagination(skip, limit)
    items = await follow_up_service.get_by_person(db, person_id)
    total = len(items)
    paginated_items = items[skip : skip + limit]
    return ListResponse(
        data=[FollowUpResponse.model_validate(f) for f in paginated_items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/project/{project_id}", response_model=ListResponse[FollowUpResponse])
async def list_by_project(
    project_id: int,
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
):
    """获取项目的跟进记录列表。"""
    skip, limit = validate_pagination(skip, limit)
    items = await follow_up_service.get_by_project(db, project_id)
    total = len(items)
    paginated_items = items[skip : skip + limit]
    return ListResponse(
        data=[FollowUpResponse.model_validate(f) for f in paginated_items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/owner/{owner_id}", response_model=ListResponse[FollowUpResponse])
async def list_by_owner(
    owner_id: int,
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
):
    """获取负责人的跟进记录列表。"""
    skip, limit = validate_pagination(skip, limit)
    items = await follow_up_service.get_by_owner(db, owner_id)
    total = len(items)
    paginated_items = items[skip : skip + limit]
    return ListResponse(
        data=[FollowUpResponse.model_validate(f) for f in paginated_items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{follow_up_id}", response_model=DataResponse[FollowUpResponse])
async def get_follow_up(
    follow_up_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """获取跟进记录详情。"""
    follow_up = await follow_up_service.get_by_id(db, follow_up_id)
    if not follow_up:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="跟进记录不存在",
        )
    return DataResponse(data=FollowUpResponse.model_validate(follow_up))


@router.delete("/{follow_up_id}", response_model=MessageResponse)
async def delete_follow_up(
    follow_up_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """删除跟进记录。"""
    success = await follow_up_service.delete(db, follow_up_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="跟进记录不存在",
        )
    return MessageResponse(message="删除成功")
