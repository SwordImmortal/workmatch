"""统计 API 端点。"""

from datetime import date, datetime

from fastapi import APIRouter, HTTPException, Query

from app.schemas.common import DataResponse
from app.services.statistics import StatisticsService
from app.utils.deps import CurrentUser, DBSession

router = APIRouter(prefix="/statistics", tags=["数据统计"])
stats_service = StatisticsService()


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
