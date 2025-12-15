from .crud import question_bank_crud
from .schemas import QuestionBankCreate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request

from app.modules.users.models import User
from app.modules.exams.crud import exam_question_crud


class QuestionBankService:
    # create new question (check first if the question with the same title and created_by is exists)
    async def create_question(
        self,
        request: Request,
        db: AsyncSession,
        question: QuestionBankCreate,
        user: User,
    ):
        active_branch_id = request.state.active_branch_id

        if not active_branch_id:
            raise HTTPException(status_code=400, detail="لم يتم اضافتك على فرع معين")

        existing_question = await question_bank_crud.get_by_title_and_creator(
            db, question.title, user.id
        )
        if existing_question:
            raise HTTPException(status_code=400, detail="هذا السؤال موجود بالفعل")
        return await question_bank_crud.create(db, question, user, active_branch_id)

    # get all questions service with option with_shared
    async def get_all_questions(
        self, db: AsyncSession, user: User, with_shared: bool = False
    ):
        questions = await question_bank_crud.get_all(db, user, with_shared)
        print(questions, "questions")
        return questions

    # get question by id
    async def get_question_by_id(self, db: AsyncSession, question_id: int, user: User):
        question = await question_bank_crud.get_by_id(db, question_id, user, True)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question

    # update question
    async def update_question(
        self,
        db: AsyncSession,
        question_id: int,
        question: QuestionBankCreate,
        user: User,
    ):
        existing_question = await question_bank_crud.get_by_id(
            db, question_id, user, False
        )
        if not existing_question:
            raise HTTPException(status_code=404, detail="Question not found")
        # check if there is another question with the same title
        existing_question_with_title = (
            await question_bank_crud.get_by_title_and_creator(
                db, question.title, user.id
            )
        )
        if (
            existing_question_with_title
            and existing_question_with_title.id != question_id
        ):
            raise HTTPException(
                status_code=400, detail="Question with the same title already exists"
            )
        # check if the exam used in any exams or not
        exam_question = await exam_question_crud.get_exam_questions_by_question_id(
            db, question_id=question_id
        )
        if exam_question:
            raise HTTPException(
                status_code=400,
                detail="لا يمكن تعديل السؤال لانه مستخدم فى امتحان",
            )
        # update question
        return await question_bank_crud.update(db, existing_question, question)

    # delete question
    async def delete_question(self, db: AsyncSession, question_id: int, user: User):
        question = await question_bank_crud.get_by_id(db, question_id, user, False)
        if not question:
            raise HTTPException(status_code=404, detail="هذا السؤال غير موجود")

        exam_question = await exam_question_crud.get_exam_questions_by_question_id(
            db, question_id=question_id
        )
        if exam_question:
            raise HTTPException(
                status_code=400,
                detail="لا يمكن حذف السؤال لانه مستخدم فى امتحان",
            )
        await question_bank_crud.delete(db, question_id)


question_bank_service = QuestionBankService()
