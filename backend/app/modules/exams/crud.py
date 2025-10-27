from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.modules.exams import models, schemas


async def create_exam(db: AsyncSession, exam_in: schemas.ExamCreate):
    exam = models.Exam(
        title=exam_in.title,
        description=exam_in.description,
        created_by=exam_in.created_by,
        created_at=datetime.utcnow(),
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


async def get_exams(db: AsyncSession):
    result = await db.execute(select(models.Exam))
    return result.scalars().all()
