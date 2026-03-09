"""提醒 API 端点。"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, validate_pagination
from app.schemas.common import DataResponse, ListResponse, MessageResponse
from app.schemas.reminder import ReminderCreate, ReminderResponse, ReminderUpdate
from app.services.reminder import ReminderService
from app.utils.deps import CurrentUser, DBSession

router = APIRouter(prefix="/reminders", tags=["提醒管理"])
reminder_service = ReminderService()


@router.post("/", response_model=DataResponse[ReminderResponse], status_code=status.HTTP_201_CREATED)
async def create_reminder(
    data: ReminderCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """创建提醒。"""
    reminder = await reminder_service.create(db, data)
    return DataResponse(data=ReminderResponse.model_validate(reminder))


@router.get("/", response_model=ListResponse[ReminderResponse])
async def list_reminders(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
    status_filter: str | None = Query(None, alias="status", description="状态筛选"),
    created_by: int | None = Query(None, description="创建者筛选"),
):
    """获取提醒列表。"""
    skip, limit = validate_pagination(skip, limit)
    reminders, total = await reminder_service.get_list(
        db,
        skip=skip,
        limit=limit,
        status=status_filter,
        created_by=created_by,
    )
    return ListResponse(
        data=[ReminderResponse.model_validate(r) for r in reminders],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/pending", response_model=ListResponse[ReminderResponse])
async def list_pending(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
):
    """获取待处理提醒（当前用户的）。"""
    skip, limit = validate_pagination(skip, limit)
    items = await reminder_service.get_pending(db, created_by=current_user.id)
    total = len(items)
    paginated_items = items[skip : skip + limit]
    return ListResponse(
        data=[ReminderResponse.model_validate(r) for r in paginated_items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{reminder_id}", response_model=DataResponse[ReminderResponse])
async def get_reminder(
    reminder_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """获取提醒详情。"""
    reminder = await reminder_service.get_by_id(db, reminder_id)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在",
        )
    return DataResponse(data=ReminderResponse.model_validate(reminder))


@router.put("/{reminder_id}", response_model=DataResponse[ReminderResponse])
async def update_reminder(
    reminder_id: int,
    data: ReminderUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """更新提醒状态。"""
    reminder = await reminder_service.update_status(db, reminder_id, data.status)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在",
        )
    return DataResponse(data=ReminderResponse.model_validate(reminder))


@router.post("/{reminder_id}/complete", response_model=DataResponse[ReminderResponse])
async def complete_reminder(
    reminder_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """标记提醒为已完成。"""
    from app.models.enums import ReminderStatus

    reminder = await reminder_service.update_status(
        db, reminder_id, ReminderStatus.COMPLETED
    )
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在",
        )
    return DataResponse(data=ReminderResponse.model_validate(reminder))


@router.post("/{reminder_id}/dismiss", response_model=DataResponse[ReminderResponse])
async def dismiss_reminder(
    reminder_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """忽略提醒。"""
    from app.models.enums import ReminderStatus

    reminder = await reminder_service.update_status(
        db, reminder_id, ReminderStatus.DISMISSED
    )
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在",
        )
    return DataResponse(data=ReminderResponse.model_validate(reminder))


@router.delete("/{reminder_id}", response_model=MessageResponse)
async def delete_reminder(
    reminder_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """删除提醒。"""
    success = await reminder_service.delete(db, reminder_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在",
        )
    return MessageResponse(message="删除成功")
