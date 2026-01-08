from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request, status
from app.modules.exams.crud.exam import exam_crud
from app.modules.exams.models.exam import Exam, ExamStatus
from app.modules.exams.schemas.exam import ExamCreate, ExamUpdate
from app.modules.question_bank.crud import question_bank_crud
from app.modules.exams.crud.exam_question import exam_question_crud

from app.modules.users.models import User
from app.modules.classes.crud import class_crud


class ExamService:
    async def create_exam(
        self, db: AsyncSession, exam_in: ExamCreate, user: User, request: Request
    ) -> Exam:
        active_branch_id = request.state.active_branch_id
        # check if the class is exists
        class_obj = await class_crud.get_by_id(db, class_id=exam_in.class_id)
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Class not found"
            )

        # check if the class's branch is the same as the user's branch
        if class_obj.branch_id != active_branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="غير مصرح لك انشاء امتحان فى هذا الفصل",
            )

        # check if exam is exists with the same title and class_id
        existing_exam = await exam_crud.get_by_title_and_class(
            db, title=exam_in.title, class_id=exam_in.class_id
        )
        if existing_exam:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="يوجد امتحان بهذا العنوان فى هذا الفصل مسبقا",
            )

        questions_in = exam_in.questions

        order_set = set()
        for question_in in questions_in:
            # check for dublicate order in questions
            if question_in.order in order_set:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate order value {question_in.order}",
                )
            order_set.add(question_in.order)

            # check if question exists in question bank
            question = await question_bank_crud.get_by_id(
                db, question_id=question_in.question_id, user=user
            )
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question with ID {question_in.question_id} not found in question bank",
                )
        # Recalculate total marks
        total_marks = sum(q.marks for q in questions_in)

        exam = await exam_crud.create(db, exam_in, user, active_branch_id, total_marks)

        await exam_question_crud.create_mult_questions(
            db,
            obj_in=questions_in,
            exam_id=exam.id,
            user=user,
            active_branch_id=active_branch_id,
        )

        return exam

    async def get_exam(self, db: AsyncSession, id: int, user: User) -> Exam:
        exam = await exam_crud.get(db, id=id, user=user)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        return exam

    async def get_take_exam(self, db: AsyncSession, user: User, exam_id: int):
        exam_attempt = await exam_crud.get_take_exam(db, user, exam_id)
        if not exam_attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="الامتحان غير موجود"
            )
        start_time = exam_attempt.start_time
        duration = exam_attempt.exam.duration_minutes
        end_time = start_time + timedelta(minutes=duration)
        if end_time < datetime.now().astimezone(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="انتهى وقت الامتحان",
            )

        return exam_attempt

    async def get_all_exams(
        self,
        db: AsyncSession,
        user: User,
        request: Request,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ):
        return await exam_crud.get_multi(db, user, request, search, sort_by, sort_order)

    async def get_available_exams(self, db: AsyncSession, user: User):
        return await exam_crud.get_available_exams(db, user)

    async def update_exam(
        self,
        db: AsyncSession,
        id: int,
        exam_in: ExamUpdate,
        user: User,
        request: Request,
    ):
        exam = await self.get_exam(db, id=id, user=user)
        active_branch_id = request.state.active_branch_id
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )

        if exam.status != ExamStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only edit exams in draft status",
            )
        total_marks = exam.total_marks
        # update exam questions with the new ones
        if exam_in.questions:
            questions_in = exam_in.questions
            order_set = set()
            for question_in in questions_in:
                if question_in.order in order_set:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Duplicate order value {question_in.order}",
                    )
                order_set.add(question_in.order)

                question = await question_bank_crud.get_by_id(
                    db, question_id=question_in.question_id, user=user
                )
                if not question:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Question with ID {question_in.question_id} not found in question bank",
                    )

            # Recalculate total marks for the update
            total_marks = sum(q.marks for q in questions_in)
            await exam_question_crud.delete_all_questions_from_exam(db, exam_id=id)

            await exam_question_crud.create_mult_questions(
                db,
                obj_in=questions_in,
                exam_id=exam.id,
                user=user,
                active_branch_id=active_branch_id,
            )

        db.expire(exam)
        await exam_crud.update(db, db_obj=exam, obj_in=exam_in, total_marks=total_marks)

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
                detail="يمكنك حذف الامتحان فقط اذا لم يتم نشره",
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
                detail="يجب ان يحتوى الامتحان على سؤال واحد على الاقل",
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
