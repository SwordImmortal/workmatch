"""项目 API 端点。"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, validate_pagination
from app.schemas.common import DataResponse, ListResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import ProjectService
from app.utils.deps import CurrentUser, DBSession

router = APIRouter(prefix="/projects", tags=["项目管理"])
project_service = ProjectService()


@router.post("/", response_model=DataResponse[ProjectResponse], status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """创建项目。"""
    try:
        project = await project_service.create(db, data)
        return DataResponse(data=ProjectResponse.model_validate(project))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=ListResponse[ProjectResponse])
async def list_projects(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页记录数"),
    enterprise_id: int | None = Query(None, description="企业ID筛选"),
    name: str | None = Query(None, description="项目名称搜索"),
    status_filter: str | None = Query(None, alias="status", description="状态筛选"),
):
    """获取项目列表。"""
    skip, limit = validate_pagination(skip, limit)
    projects, total = await project_service.get_list(
        db,
        skip=skip,
        limit=limit,
        enterprise_id=enterprise_id,
        name=name,
        status=status_filter,
    )
    return ListResponse(
        data=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{project_id}", response_model=DataResponse[ProjectResponse])
async def get_project(
    project_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """获取项目详情。"""
    project = await project_service.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在",
        )
    return DataResponse(data=ProjectResponse.model_validate(project))


@router.put("/{project_id}", response_model=DataResponse[ProjectResponse])
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """更新项目信息。"""
    try:
        project = await project_service.update(db, project_id, data)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在",
            )
        return DataResponse(data=ProjectResponse.model_validate(project))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """删除项目。"""
    success = await project_service.delete(db, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在",
        )
