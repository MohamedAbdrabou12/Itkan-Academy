from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db
from app.modules.exams import crud, schemas

router = APIRouter()


@router.post("/", response_model=schemas.ExamOut)
def create_exam(exam_in: schemas.ExamCreate, db: Session = Depends(get_db)):
    return crud.create_exam(db, exam_in)


@router.get("/", response_model=list[schemas.ExamOut])
def list_exams(db: Session = Depends(get_db)):
    return crud.get_exams(db)
