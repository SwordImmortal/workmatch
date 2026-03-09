"""API v1 路由汇总。"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    enterprises,
    follow_ups,
    person_projects,
    persons,
    projects,
    reminders,
    statistics,
)

api_router = APIRouter()

# 认证路由
api_router.include_router(auth.router)

# 业务路由
api_router.include_router(persons.router)
api_router.include_router(enterprises.router)
api_router.include_router(projects.router)
api_router.include_router(person_projects.router)
api_router.include_router(follow_ups.router)
api_router.include_router(reminders.router)
api_router.include_router(statistics.router)
