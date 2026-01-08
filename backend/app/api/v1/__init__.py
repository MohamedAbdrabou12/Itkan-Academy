# backend/app/api/v1/__init__.py
from app.api.v1.auth.auth import auth_router
from app.modules.audits.router import audit_log_router
from app.modules.branches.router import branch_router
from app.modules.classes.router import classes_router
from app.modules.curriculums.router.curriculum import curriculums_router
from app.modules.curriculums.router.subject import subjects_router
from app.modules.evaluations.router import evaluations_router
from app.modules.exams.router.exam import exam_router
from app.modules.exams.router.exam_answer import exam_answers_router
from app.modules.exams.router.exam_attempt import exam_attempts_router
from app.modules.exams.router.exam_question import exam_question_router
from app.modules.financial.router.invoice import invoice_router
from app.modules.financial.router.payment import payment_router
from app.modules.notifications.router import notification_router
from app.modules.parents.router import parents_router
from app.modules.permissions.router import permissions_router
from app.modules.question_bank.router import question_bank_router
from app.modules.reports.router.base import reports_router
from app.modules.role_permissions.router import role_permissions_router
from app.modules.roles.router import role_router
from app.modules.student_progress.router import student_progress_router
from app.modules.students.router import students_router
from app.modules.teachers.router import teachers_router
from app.modules.users.router import user_router
from fastapi import APIRouter

# Initialize API Router
api_router = APIRouter()

# Include sub-routers with tags for Swagger grouping
api_router.include_router(audit_log_router, tags=["Audit Logs"])
api_router.include_router(auth_router, tags=["Public Auth"])
api_router.include_router(branch_router, tags=["Branches"])
api_router.include_router(classes_router, tags=["Classes"])
api_router.include_router(curriculums_router, tags=["Curriculums"])
api_router.include_router(evaluations_router, tags=["Daily Evaluations"])
api_router.include_router(exam_answers_router, tags=["Exam Answers"])
api_router.include_router(exam_attempts_router, tags=["Exam Attempts"])
api_router.include_router(exam_question_router, tags=["Exam Questions"])
api_router.include_router(exam_router, tags=["Exams"])
api_router.include_router(invoice_router, tags=["Invoices"])
api_router.include_router(notification_router, tags=["Notifications"])
api_router.include_router(parents_router, tags=["Parents"])
api_router.include_router(payment_router, tags=["Payments"])
api_router.include_router(permissions_router, tags=["Permissions"])
api_router.include_router(question_bank_router, tags=["Question Bank"])
api_router.include_router(reports_router, tags=["Reports"])
api_router.include_router(role_permissions_router, tags=["Role Permissions"])
api_router.include_router(role_router, tags=["Roles"])
api_router.include_router(students_router, tags=["Students"])
api_router.include_router(student_progress_router, tags=["Student Progress"])
api_router.include_router(subjects_router, tags=["Subjects"])
api_router.include_router(teachers_router, tags=["Teachers"])
api_router.include_router(user_router, tags=["Admin Users"])
