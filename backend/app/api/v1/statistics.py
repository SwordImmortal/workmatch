"""统计 API 端点。"""

from datetime import date, datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.schemas.common import DataResponse
from app.schemas.statistics import OverviewStats
from app.services.statistics import StatisticsService
from app.services.excel_export import excel_export_service
from app.utils.deps import CurrentUser, DBSession

router = APIRouter(prefix="/statistics", tags=["数据统计"])
stats_service = StatisticsService()


@router.get("/overview", response_model=DataResponse[OverviewStats])
async def get_overview(
    db: DBSession,
    current_user: CurrentUser,
    project_id: int | None = Query(None, description="项目ID（可选，不传则全局）"),
):
    """获取整体概览统计。"""
    stats = await stats_service.get_overview(
        db,
        project_id=project_id,
        user_id=current_user.id if current_user.role == "recruiter" else None,
    )
    return DataResponse(data=OverviewStats(**stats))


@router.get("/project/{project_id}/funnel", response_model=DataResponse)
async def get_project_funnel(
    project_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """获取项目漏斗数据。"""
    stats = await stats_service.get_project_funnel(db, project_id)
    return DataResponse(data=stats)


@router.get("/project/{project_id}/daily", response_model=DataResponse)
async def get_daily_statistics(
    project_id: int,
    db: DBSession,
    current_user: CurrentUser,
    target_date: date = Query(..., description="统计日期"),
):
    """获取每日统计数据。"""
    stats = await stats_service.get_daily_statistics(
        db,
        project_id,
        datetime.combine(target_date, datetime.min.time()),
    )
    return DataResponse(data=stats)


@router.get("/project/{project_id}/range", response_model=DataResponse)
async def get_range_statistics(
    project_id: int,
    db: DBSession,
    current_user: CurrentUser,
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
):
    """获取日期范围统计数据。"""
    stats = await stats_service.get_date_range_statistics(
        db,
        project_id,
        datetime.combine(start_date, datetime.min.time()),
        datetime.combine(end_date, datetime.min.time()),
    )
    return DataResponse(data=stats)


@router.get("/project/{project_id}/fail-reasons", response_model=DataResponse)
async def get_fail_reason_breakdown(
    project_id: int,
    db: DBSession,
    current_user: CurrentUser,
):
    """获取失败原因分布。"""
    stats = await stats_service.get_fail_reason_breakdown(db, project_id)
    return DataResponse(data=stats)


@router.get("/project/{project_id}/export")
async def export_statistics(
    project_id: int,
    db: DBSession,
    current_user: CurrentUser,
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
):
    """导出项目统计数据。"""
    # 获取各维度数据
    funnel_data = await stats_service.get_project_funnel(db, project_id)
    daily_data = await stats_service.get_date_range_statistics(
        db,
        project_id,
        datetime.combine(start_date, datetime.min.time()),
        datetime.combine(end_date, datetime.min.time()),
    )
    fail_reasons = await stats_service.get_fail_reason_breakdown(db, project_id)

    # 导出
    output = await excel_export_service.export_statistics(
        db,
        project_id,
        datetime.combine(start_date, datetime.min.time()),
        datetime.combine(end_date, datetime.min.time()),
        funnel_data,
        daily_data,
        fail_reasons,
    )

    filename = f"项目统计_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
