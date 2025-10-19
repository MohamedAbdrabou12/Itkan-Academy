from sqlalchemy.orm import Session
from datetime import datetime
from app.modules.exams import models, schemas


def create_exam(db: Session, exam_in: schemas.ExamCreate):
    exam = models.Exam(
        title=exam_in.title,
        description=exam_in.description,
        created_by=exam_in.created_by,
        created_at=datetime.utcnow(),
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


def get_exams(db: Session):
    return db.query(models.Exam).all()
