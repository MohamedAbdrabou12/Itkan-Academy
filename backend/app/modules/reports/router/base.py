from app.modules.reports.router.students import student_reports_router
from fastapi import APIRouter

reports_router = APIRouter(prefix="/reports", tags=["Reports"])
reports_router.include_router(student_reports_router)
