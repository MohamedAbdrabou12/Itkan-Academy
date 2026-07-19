from collections.abc import Sequence

from app.modules.enrolments.models import enrolment as models
from app.modules.enrolments.models.pricing_plan import EnrolmentPricingPlan
from app.modules.enrolments.schemas import enrolment as schemas
from app.modules.users.models import User
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class EnrolmentCrud:
    def create(self, db: AsyncSession, data: schemas.EnrolmentCreate) -> models.Enrolment:
        enrolment = models.Enrolment(
            pricing_plan_id=data.pricing_plan_id,
            student_id=data.student_id,
            months_paid=data.months_paid,
        )
        db.add(enrolment)
        return enrolment

    async def exists_by_curriculum_and_student_id(
        self, db: AsyncSession, curriculum_id: int, student_id: int
    ) -> bool:
        query_result = await db.execute(
            select(func.count())
            .select_from(models.Enrolment)
            .join(EnrolmentPricingPlan, EnrolmentPricingPlan.id == models.Enrolment.pricing_plan_id)
            .where(
                and_(
                    EnrolmentPricingPlan.curriculum_id == curriculum_id,
                    models.Enrolment.student_id == student_id,
                )
            )
        )
        return query_result.scalar_one() != 0

    async def get_all(
        self,
        db: AsyncSession,
        search: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> Sequence[models.Enrolment]:
        query = (
            select(
                models.Enrolment.id,
                models.Enrolment.pricing_plan_id,
                models.Enrolment.student_id,
                models.Enrolment.months_paid,
                EnrolmentPricingPlan.name.label("pricing_plan_name"),
                EnrolmentPricingPlan.start_month,
                EnrolmentPricingPlan.end_month,
                User.full_name.label("student_full_name"),
            )
            .select_from(models.Enrolment)
            .join(User, models.Enrolment.student_id == User.id)
            .join(EnrolmentPricingPlan, models.Enrolment.pricing_plan_id == EnrolmentPricingPlan.id)
        )

        if search:
            search = "%" + search + "%"
            query = query.where(
                or_(User.full_name.ilike(search), EnrolmentPricingPlan.name.ilike(search))
            )

        sort_columns = {
            "id": models.Enrolment.id,
            "pricing_plan_id": models.Enrolment.pricing_plan_id,
            "pricing_plan_name": EnrolmentPricingPlan.name,
            "student_id": models.Enrolment.student_id,
            "student_full_name": User.full_name,
        }

        sort_column = sort_columns.get(sort_by, models.Enrolment.id)
        query = query.order_by(
            sort_column.desc() if sort_order.lower() == "desc" else sort_column.asc()
        )

        return await paginate(db, query)  # pyright: ignore[reportAny]

    async def get_by_id(self, db: AsyncSession, id: int) -> models.Enrolment | None:
        query_result = await db.execute(
            select(models.Enrolment)
            .options(joinedload(models.Enrolment.pricing_plan))
            .where(models.Enrolment.id == id)
        )
        return query_result.scalar_one_or_none()

    async def update(self, db: AsyncSession, id: int, data: schemas.EnrolmentUpdate):
        _ = await db.execute(
            update(models.Enrolment).where(models.Enrolment.id == id).values(**data.model_dump())
        )

    async def delete(self, db: AsyncSession, id: int):
        _ = await db.execute(delete(models.Enrolment).where(models.Enrolment.id == id))


enrolment_crud = EnrolmentCrud()
