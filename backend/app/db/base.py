# ruff: noqa: E402, F401, F811
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can detect them
from app.modules.attendance import models
from app.modules.audits import models
from app.modules.audits.models import AuditLog
from app.modules.branches import models
from app.modules.classes import models
from app.modules.curriculums.models import curriculum, subject, unit, unit_item
from app.modules.evaluations.models import Evaluation
from app.modules.exams.models.exam import Exam
from app.modules.exams.models.exam_answer import ExamAnswer
from app.modules.exams.models.exam_attempt import ExamAttempt
from app.modules.exams.models.exam_question import ExamQuestion
from app.modules.financial.models.invoice import Invoice
from app.modules.financial.models.payment import Payment
from app.modules.notifications import models
from app.modules.parents.models import Parent, ParentStudent
from app.modules.permissions.models import Permission
from app.modules.question_bank import models
from app.modules.role_permissions.models import RolePermission
from app.modules.roles import models
from app.modules.student_progress import models
from app.modules.students import models
from app.modules.teachers import models
from app.modules.users import models
