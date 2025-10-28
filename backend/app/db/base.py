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
