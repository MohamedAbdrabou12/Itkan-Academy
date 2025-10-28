# app/db/base.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# all models so Alembic can detect them
from app.modules.users import models  # noqa
from app.modules.branches import models  # noqa
from app.modules.exams import models  # noqa
from app.modules.financial import models  # noqa
from app.modules.reports import models  # noqa
from app.modules.roles import models  # noqa
from app.modules.permissions import models  # noqa
from app.modules.classes import models  # noqa
from app.modules.students import models  # noqa
from app.modules.audits import models  # noqa
from app.modules.attendance import models  # noqa
from app.modules.notifications import models  # noqa
from app.modules.question_bank import models  # noqa
from app.modules.evaluations import models  # noqa
