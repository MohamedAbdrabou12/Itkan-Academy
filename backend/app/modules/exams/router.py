from typing import AsyncGenerator
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.modules.exams import crud, schemas

router = APIRouter()


# Async database dependency returning an AsyncGenerator to satisfy Pylance
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@router.post("/", response_model=schemas.ExamOut)
async def create_exam(exam_in: schemas.ExamCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_exam(db, exam_in)


@router.get("/", response_model=list[schemas.ExamOut])
async def list_exams(db: AsyncSession = Depends(get_db)):
    return await crud.get_exams(db)
