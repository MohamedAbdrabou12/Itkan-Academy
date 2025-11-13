from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime, timezone
from app.modules.exams.crud.exam import exam_crud
from app.modules.exams.crud.exam_question import exam_question_crud
from app.modules.exams.crud.exam_attempt import exam_attempt_crud

from app.modules.users.models import User
from app.modules.exams.models.exam_attempt import ExamAttemptStatus
from app.modules.exams.schemas.exam_attempt import ExamAttemptUpdate
from app.modules.exams.schemas.exam_answer import (
    ExamAnswerBulkCreate,
    ExamAnswerBulkItemSubmit,
)
from app.modules.exams.crud.exam_answer import exam_answer_crud


class ExamAnswerService:
    async def submit_answers_bulk(
        self,
        db: AsyncSession,
        attempt_id: int,
        answers_in: ExamAnswerBulkCreate,
        user: User,
    ):
        attempt = await exam_attempt_crud.get_with_user(db, attempt_id, user)

        if not attempt:
            raise HTTPException(status_code=404, detail="Exam attempt not found")
        if attempt.student_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to submit answers for this attempt",
            )
        if attempt.status != ExamAttemptStatus.STARTED:
            raise HTTPException(
                status_code=400,
                detail="Cannot submit answers for an exam that is not in progress",
            )

        # check if the exam exists
        exam = await exam_crud.get(db, attempt.exam_id, user)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")

        # check if the exam answer is not submitted after the end date of the exam
        exam_end_time = exam.end_time
        if exam_end_time is None:
            raise HTTPException(
                status_code=400,
                detail="Exam end time is not set. Cannot submit answers.",
            )
        if exam_end_time < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=400,
                detail="Cannot submit answers after the exam end time",
            )

        # Validate that all questions in the bulk submission belong to the exam of this attempt
        exam_questions = await exam_question_crud.get_multi_by_exam(
            db, exam_id=attempt.exam_id
        )
        exam_question_ids = {q.question_id for q in exam_questions}

        for answer_item in answers_in.answers:
            if answer_item.question_id not in exam_question_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Question ID {answer_item.question_id} does not belong to this exam.",
                )

        # in the mcq question, check if it's value is one of the options
        for answer_item in answers_in.answers:
            question = next(
                (q for q in exam_questions if q.question_id == answer_item.question_id),
                None,
            )
            if question and question.question.type == "mcq":
                options = question.question.options or []
                if answer_item.selected_option not in options:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Selected option '{answer_item.selected_option}' is not valid for question ID {answer_item.question_id}.",
                    )

        # change exam_attempt status to submitted and set the end-time
        attempt_update = ExamAttemptUpdate(
            status=ExamAttemptStatus.SUBMITTED, end_time=datetime.now(timezone.utc)
        )
        await exam_attempt_crud.update(db, db_obj=attempt, obj_in=attempt_update)

        answers = answers_in.answers
        answers_with_marks = []

        # set the marks if the question type is mcq and has the correct answer
        for answer in answers:
            question = next(
                (q for q in exam_questions if q.question_id == answer.question_id),
                None,
            )
            if question and question.question.type == "mcq":
                if (
                    question.question.correct_answer is not None
                    and answer.selected_option == question.question.correct_answer
                ):
                    answer_with_mark = ExamAnswerBulkItemSubmit(
                        **answer.model_dump(), marks_obtained=question.marks
                    )
                    answers_with_marks.append(answer_with_mark)
                else:
                    answer_with_mark = ExamAnswerBulkItemSubmit(
                        **answer.model_dump(), marks_obtained=0
                    )
                    answers_with_marks.append(answer_with_mark)
            else:
                answers_with_marks.append(answer)

        return await exam_answer_crud.create_bulk(
            db, attempt_id=attempt_id, answers_in=answers_with_marks
        )


exam_answers_service = ExamAnswerService()
