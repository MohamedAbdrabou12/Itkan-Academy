# app/db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can detect them
from app.modules.users import models  # noqa
from app.modules.branches import models  # noqa
from app.modules.roles import models  # noqa
from app.modules.permissions.models.permission import Permission  # noqa
from app.modules.permissions.models.permission_role import RolePermission  # noqa
from app.modules.audits.models.audit_log import AuditLog  # noqa
from app.modules.classes import models  # noqa
from app.modules.students import models  # noqa
from app.modules.audits import models  # noqa
from app.modules.attendance import models  # noqa
from app.modules.notifications import models  # noqa
from app.modules.question_bank import models  # noqa
from app.modules.evaluations.models.daily_evaluation import DailyEvaluation  # noqa
from app.modules.staff import models  # noqa
from app.modules.exams.models.exam_attempt import ExamAttempt  # noqa
from app.modules.exams.models.exam_answer import ExamAnswer  # noqa
from app.modules.exams.models.exam_question import ExamQuestion  # noqa
from app.modules.exams.models.exam import Exam  # noqa
from app.modules.financial.models.invoice import Invoice  # noqa
from app.modules.financial.models.payment import Payment  # noqa
from app.modules.reports.models.report_job import ReportJob  # noqa
