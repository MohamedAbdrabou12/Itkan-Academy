from .crud import question_bank_crud
from .schemas import QuestionBankCreate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.modules.users.models import User


class QuestionBankService:
    # create new question (check first if the question with the same title and created_by is exists)
    async def create_question(
        self, db: AsyncSession, question: QuestionBankCreate, user: User
    ):
        existing_question = await question_bank_crud.get_by_title_and_creator(
            db, question.title, user.id
        )
        if existing_question:
            raise HTTPException(
                status_code=400, detail="Question with the same title already exists"
            )
        return await question_bank_crud.create(db, question, user)

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
        # update question
        return await question_bank_crud.update(db, existing_question, question)


question_bank_service = QuestionBankService()
