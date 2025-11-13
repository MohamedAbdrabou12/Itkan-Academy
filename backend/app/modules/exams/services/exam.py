from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.modules.exams.crud.exam import exam_crud
from app.modules.exams.models.exam import Exam, ExamStatus
from app.modules.exams.schemas.exam import ExamCreate, ExamUpdate

from app.modules.users.models import User
from app.modules.classes.crud import class_crud


class ExamService:
    async def create_exam(
        self, db: AsyncSession, exam_in: ExamCreate, user: User
    ) -> Exam:
        # check if the class is exists
        class_obj = await class_crud.get_by_id(db, class_id=exam_in.class_id)
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
            )

        # check if the class's branch is the same as the user's branch
        if class_obj.branch_id != user.branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create exam for a class in another branch",
            )

        # check if exam is exists with the same title and class_id
        existing_exam = await exam_crud.get_by_title_and_class(
            db, title=exam_in.title, class_id=exam_in.class_id
        )
        if existing_exam:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam with the same title already exists for this class",
            )

        return await exam_crud.create(db, exam_in, user)

    async def get_exam(self, db: AsyncSession, id: int, user: User) -> Exam:
        exam = await exam_crud.get(db, id=id, user=user)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        return exam

    async def get_all_exams(self, db: AsyncSession, user: User):
        return await exam_crud.get_multi(db, user)

    async def update_exam(
        self, db: AsyncSession, id: int, exam_in: ExamUpdate, user: User
    ) -> Exam:
        exam = await self.get_exam(db, id=id, user=user)
        if exam.status != ExamStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only edit exams in draft status",
            )
        # Add more permission checks here based on user role
        return await exam_crud.update(db, db_obj=exam, obj_in=exam_in)

    async def delete_exam(self, db: AsyncSession, *, id: int, user: User):
        exam = await self.get_exam(db, id=id, user=user)

        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )

        # delete only in draft status
        if exam.status != ExamStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only delete exams in draft status",
            )

        return await exam_crud.delete(db, id=id, user=user)

    async def publish_exam(self, db: AsyncSession, id: int, user: User) -> Exam:
        exam = await self.get_exam(db, id=id, user=user)
        if exam.status != ExamStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam is not in draft status",
            )

        # check if exam has questions
        if not exam.questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam must have at least one question",
            )

        return await exam_crud.publich_exam(db, db_obj=exam)

    async def close_exam(self, db: AsyncSession, id: int, user: User) -> Exam:
        exam = await self.get_exam(db, id=id, user=user)
        if exam.status == ExamStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Exam is already closed"
            )
        if exam.status != ExamStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only published exams can be closed",
            )
        return await exam_crud.close_exam(db, db_obj=exam)


exam_service = ExamService()
