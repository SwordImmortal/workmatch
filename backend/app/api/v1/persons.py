"""人员 API 端点。"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, validate_pagination
from app.schemas.common import DataResponse, ListResponse
from app.schemas.person import PersonCreate, PersonResponse, PersonUpdate, PersonWithProjectsResponse
from app.services.person import PersonService
from app.utils.deps import CurrentUser, DBSession

router = APIRouter(prefix="/persons", tags=["人员管理"])
person_service = PersonService()


@router.post("/", response_model=DataResponse[PersonResponse], status_code=status.HTTP_201_CREATED)
async def create_person(
    data: PersonCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """创建人员。"""
    try:
        person = await person_service.create(db, data, created_by=current_user.id)
        return DataResponse(data=PersonResponse.model_validate(person))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=ListResponse[PersonResponse])
async def list_persons(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
    city: str | None = Query(None, description="城市筛选"),
    source: str | None = Query(None, description="来源筛选"),
    reusable: bool | None = Query(None, description="是否可复用"),
    search: str | None = Query(None, description="搜索姓名/手机号"),
):
    """获取人员列表。"""
    skip, limit = validate_pagination(skip, limit)
    persons, total = await person_service.get_list(
        db,
        skip=skip,
        limit=limit,
        city=city,
        source=source,
        reusable=reusable,
        search=search,
    )
    return ListResponse(
        data=[PersonResponse.model_validate(p) for p in persons],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{person_id}", response_model=DataResponse[PersonResponse])
async def get_person(
    person_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """获取人员详情。"""
    person = await person_service.get_by_id(db, person_id, current_user)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="人员不存在",
        )
    return DataResponse(data=PersonResponse.model_validate(person))


@router.get("/{person_id}/projects", response_model=DataResponse[PersonWithProjectsResponse])
async def get_person_with_projects(
    person_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """获取人员及其项目状态。"""
    person = await person_service.get_with_projects(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="人员不存在",
        )
    return DataResponse(data=PersonWithProjectsResponse.model_validate(person))


@router.put("/{person_id}", response_model=DataResponse[PersonResponse])
async def update_person(
    person_id: int,
    data: PersonUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """更新人员信息。"""
    try:
        person = await person_service.update(db, person_id, data, current_user)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="人员不存在",
            )
        return DataResponse(data=PersonResponse.model_validate(person))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """删除人员。"""
    success = await person_service.delete(db, person_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="人员不存在",
        )
