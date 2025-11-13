from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.modules.exams.crud.exam import exam_crud
from app.modules.exams.crud.exam_question import exam_question_crud
from app.modules.exams.models.exam import Exam, ExamStatus
from app.modules.exams.schemas.exam_question import (
    ExamQuestionCreate,
    ExamQuestionUpdate,
)
from app.modules.users.models import User
from app.modules.question_bank.crud import question_bank_crud


class ExamQuestionService:
    async def add_questions_to_exam(
        self,
        db: AsyncSession,
        exam_id: int,
        questions_in: list[ExamQuestionCreate],
        user: User,
    ):
        exam = await exam_crud.get(db, id=exam_id, user=user)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        if exam.status != ExamStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only add questions to exams in draft status",
            )
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

        await exam_question_crud.create_mult_questions(
            db, obj_in=questions_in, exam_id=exam_id, user=user
        )
        # Recalculate total marks
        total_marks = sum(q.marks for q in questions_in)
        return await exam_crud.update_total_marks(
            db, db_obj=exam, total_marks=total_marks
        )

    async def add_question_to_exam(
        self,
        db: AsyncSession,
        *,
        exam_id: int,
        question_in: list[ExamQuestionCreate],
        user: User,
    ) -> Exam:
        exam = await exam_crud.get(db, id=exam_id, user=user)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        if exam.status != ExamStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only add questions to exams in draft status",
            )

        for question_data in question_in:
            question_id = question_data.question_id
            question_db = await question_bank_crud.get_by_id(
                db, question_id=question_id, user=user
            )
            if not question_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question with ID {question_id} not found in question bank",
                )

            # Check if the question is already added to the exam
            existing_exam_question = next(
                (eq for eq in exam.questions if eq.question_id == question_id),
                None,
            )
            if existing_exam_question:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question with ID {question_id} already exists in this exam",
                )

            await exam_question_crud.create(
                db, obj_in=question_data, exam_id=exam_id, user=user
            )

        exam_questions = await exam_question_crud.get_multi_by_exam(db, exam_id=exam_id)
        total_marks = sum(q.marks for q in exam_questions)
        return await exam_crud.update_total_marks(
            db, db_obj=exam, total_marks=total_marks
        )

    async def get_questions_for_exam(
        self, db: AsyncSession, *, exam_id: int, user: User
    ):
        exam = await exam_crud.get(db, id=exam_id, user=user)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        return exam.questions

    async def update_question_in_exam(
        self,
        db: AsyncSession,
        exam_id: int,
        question_id: int,
        question_in: ExamQuestionUpdate,
        user: User,
    ) -> Exam:
        exam = await exam_crud.get(db, id=exam_id, user=user)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        if exam.status != ExamStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only edit questions in draft exams",
            )

        question = await exam_question_crud.get(db, id=question_id)
        if not question or question.exam_id != exam_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found in this exam",
            )

        exam_questions = exam.questions

        # check dublicate order
        if question_in.order is not None:
            for eq in exam_questions:
                if eq.order == question_in.order and eq.id != question_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Order value {question_in.order} already exists for another question in this exam",
                    )

        await exam_question_crud.update(db, db_obj=question, obj_in=question_in)

        # Recalculate total marks
        exam_questions = await exam_question_crud.get_multi_by_exam(db, exam_id=exam_id)
        total_marks = sum(q.marks for q in exam_questions)
        return await exam_crud.update_total_marks(
            db, db_obj=exam, total_marks=total_marks
        )

    async def remove_question_from_exam(
        self, db: AsyncSession, *, exam_id: int, question_id: int, user: User
    ) -> Exam:
        exam = await exam_crud.get(db, id=exam_id, user=user)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        if exam.status != ExamStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only remove questions from draft exams",
            )

        question = await exam_question_crud.get(db, id=question_id)
        if not question or question.exam_id != exam_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found in this exam",
            )

        await exam_question_crud.delete(db, id=question_id)

        db.expire(exam)

        # Recalculate total marks
        exam_questions = await exam_question_crud.get_multi_by_exam(db, exam_id=exam_id)
        total_marks = sum(q.marks for q in exam_questions)
        return await exam_crud.update_total_marks(
            db, db_obj=exam, total_marks=total_marks
        )


exam_question_service = ExamQuestionService()
