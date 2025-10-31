# backend/app/api/v1/__init__.py
from fastapi import APIRouter

# Import routers from modules
from app.modules.users.router import router as user_router
from app.modules.roles.router import router as role_router
from app.modules.permissions.router.permission import router as permission_router
from app.modules.permissions.router.permission_role import (
    router as role_permission_router,
)
from app.api.v1.auth.auth import router as auth_router
from app.modules.branches.router import router as branch_router
from app.modules.classes.router import router as class_router
from app.modules.staff.router import router as staff_router
from app.modules.students.router import router as student_router
from app.modules.attendance.router import router as attendance_router
from app.modules.evaluations.router.daily_evaluation import (
    router as daily_evaluation_router,
)
from app.modules.audits.router.audit_log import router as audit_log_router
from app.modules.question_bank.router import router as question_bank_router
from app.modules.notifications.router import router as notification_router
from app.modules.financial.router.invoice import router as invoice_router
from app.modules.financial.router.payment import router as payment_router
from app.modules.reports.router.report_job import router as report_job_router
from app.modules.exams.router.exam import router as exam_router
from app.modules.exams.router.exam_question import router as exam_question_router
from app.modules.exams.router.exam_answer import router as exam_answer_router
from app.modules.exams.router.exam_attempt import router as exam_attempt_router

# Initialize API Router
api_router = APIRouter()

# Include sub-routers with tags for Swagger grouping
api_router.include_router(user_router, tags=["Admin Users"])
api_router.include_router(role_router, tags=["Roles"])
api_router.include_router(permission_router, tags=["Permissions"])
api_router.include_router(role_permission_router, tags=["Role Permissions"])
api_router.include_router(auth_router, tags=["Public Auth"])
api_router.include_router(branch_router, tags=["Branches"])
api_router.include_router(class_router, tags=["Classes"])
api_router.include_router(staff_router, tags=["Staff"])
api_router.include_router(student_router, tags=["Students"])
api_router.include_router(attendance_router, tags=["Attendance"])
api_router.include_router(daily_evaluation_router, tags=["Daily Evaluations"])
api_router.include_router(audit_log_router, tags=["Audit Logs"])
api_router.include_router(question_bank_router, tags=["Question Bank"])
api_router.include_router(notification_router, tags=["Notifications"])
api_router.include_router(invoice_router, tags=["Invoices"])
api_router.include_router(payment_router, tags=["Payments"])
api_router.include_router(report_job_router, tags=["Report Jobs"])
api_router.include_router(exam_router, tags=["Exams"])
api_router.include_router(exam_question_router, tags=["Exam Questions"])
api_router.include_router(exam_answer_router, tags=["Exam Answers"])
api_router.include_router(exam_attempt_router, tags=["Exam Attempts"])
