"""人员 API 端点。"""

from datetime import date, datetime

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, validate_pagination
from app.models.enums import PersonProjectStatus
from app.schemas.common import DataResponse, ListResponse
from app.schemas.person import (
    PersonCreate,
    PersonImportResult,
    PersonResponse,
    PersonUpdate,
    PersonWithProjectsResponse,
)
from app.services.person import PersonService
from app.services.excel_import import excel_import_service
from app.services.excel_export import excel_export_service
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


@router.get("/import/template")
async def download_import_template():
    """下载人员导入模板。"""
    template = excel_import_service.generate_template()
    from datetime import datetime

    filename = f"人员导入模板_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        template,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.post("/import", response_model=DataResponse[PersonImportResult])
async def import_persons(
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(..., description="Excel 文件"),
):
    """批量导入人员。"""
    # 检查文件类型
    if not file.filename or not (
        file.filename.endswith(".xlsx") or file.filename.endswith(".xls")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传 Excel 文件（.xlsx 或 .xls）",
        )

    # 读取文件内容
    content = await file.read()

    # 执行导入
    result = await excel_import_service.import_persons(
        db,
        content,
        created_by=current_user.id,
    )

    return DataResponse(data=PersonImportResult(**result))


@router.get("/export")
async def export_persons(
    db: DBSession,
    current_user: CurrentUser,
    project_id: int | None = Query(None, description="项目ID筛选"),
    status: str | None = Query(None, description="状态筛选"),
    start_date: date | None = Query(None, description="开始日期"),
    end_date: date | None = Query(None, description="结束日期"),
):
    """导出人员列表。"""
    # 状态转换
    status_filter = None
    if status:
        try:
            status_filter = PersonProjectStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值: {status}",
            )

    # 日期转换
    start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_dt = datetime.combine(end_date, datetime.min.time()) if end_date else None

    # 导出
    output = await excel_export_service.export_persons(
        db,
        project_id=project_id,
        status_filter=status_filter,
        start_date=start_dt,
        end_date=end_dt,
    )

    filename = f"人员列表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
