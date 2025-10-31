from app.api.v1.auth.auth import auth_router
from app.modules.attendance.router import attendance_router
from app.modules.audits.router import audit_log_router
from app.modules.branches.router import branch_router
from app.modules.classes.router import class_router
from app.modules.evaluations.router import daily_evaluation_router
from app.modules.exams.router.exam import exam_router
from app.modules.exams.router.exam_answer import exam_answer_router
from app.modules.exams.router.exam_attempt import exam_attempt_router
from app.modules.exams.router.exam_question import exam_question_router
from app.modules.financial.router.invoice import invoice_router
from app.modules.financial.router.payment import payment_router
from app.modules.notifications.router import notification_router
from app.modules.permissions.router import permissions_router
from app.modules.question_bank.router import question_bank_router
from app.modules.reports.router import report_job_router
from app.modules.role_permissions.router import role_permissions_router
from app.modules.roles.router import role_router
from app.modules.staff.router import staff_router
from app.modules.students.router import students_router
from app.modules.users.router import user_router
from fastapi import APIRouter

# Initialize API Router
api_router = APIRouter()

# Include sub-routers with tags for Swagger grouping
api_router.include_router(auth_router, tags=["Public Auth"])
api_router.include_router(user_router, tags=["Admin Users"])
api_router.include_router(role_router, tags=["Roles"])
api_router.include_router(permissions_router, tags=["Permissions"])
api_router.include_router(role_permissions_router, tags=["Role Permissions"])
api_router.include_router(branch_router, tags=["Branches"])
api_router.include_router(class_router, tags=["Classes"])
api_router.include_router(staff_router, tags=["Staff"])
api_router.include_router(students_router, tags=["Students"])
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
