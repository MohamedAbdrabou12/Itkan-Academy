from collections.abc import Sequence
from decimal import Decimal

from app.modules.branches.models import Branch
from app.modules.curriculums.models.curriculum import Curriculum
from app.modules.enrolments.models import pricing_plan as models
from app.modules.enrolments.models.enrolment import Enrolment
from app.modules.enrolments.schemas import pricing_plan as schemas
from app.modules.enrolments.schemas.enrolment import EnrolmentRead
from app.modules.parents.models import Parent
from app.modules.users.crud import map_user_to_read
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, not_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class EnrolmentPricingPlanCrud:
    def create(
        self, db: AsyncSession, data: schemas.EnrolmentPricingPlanCreate
    ) -> models.EnrolmentPricingPlan:
        plan = models.EnrolmentPricingPlan(
            curriculum_id=data.curriculum_id,
            branch_id=data.branch_id,
            name=data.name,
            monthly_price=Decimal(data.monthly_price),
            start_month=data.start_month,
            end_month=data.end_month,
        )

        db.add(plan)
        return plan

    async def get_all(
        self,
        db: AsyncSession,
        branch_id: int | None = None,
        search: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> Sequence[models.EnrolmentPricingPlan]:
        query = (
            select(
                models.EnrolmentPricingPlan.id,
                models.EnrolmentPricingPlan.curriculum_id,
                Curriculum.name.label("curriculum_name"),
                models.EnrolmentPricingPlan.branch_id,
                Branch.name.label("branch_name"),
                models.EnrolmentPricingPlan.name,
                models.EnrolmentPricingPlan.monthly_price,
                models.EnrolmentPricingPlan.start_month,
                models.EnrolmentPricingPlan.end_month,
            )
            .select_from(models.EnrolmentPricingPlan)
            .join(Curriculum, models.EnrolmentPricingPlan.curriculum_id == Curriculum.id)
            .join(
                Branch,
                models.EnrolmentPricingPlan.branch_id == Branch.id,
                isouter=True,
            )
        )

        if branch_id is not None:
            query = query.where(
                or_(
                    models.EnrolmentPricingPlan.branch_id == branch_id,
                    not_(models.EnrolmentPricingPlan.branch_id.has()),
                )
            )

        if search:
            search = "%" + search + "%"
            query = query.where(models.EnrolmentPricingPlan.name.ilike(search))

        sort_columns = {
            "id": models.EnrolmentPricingPlan.id,
            "curriculum_id": models.EnrolmentPricingPlan.curriculum_id,
            "curriculum_name": Curriculum.name,
            "branch_id": models.EnrolmentPricingPlan.branch_id,
            "branch_name": Branch.name,
            "name": models.EnrolmentPricingPlan.name,
            "monthly_price": models.EnrolmentPricingPlan.monthly_price,
            "start_month": models.EnrolmentPricingPlan.start_month,
            "end_month": models.EnrolmentPricingPlan.end_month,
        }

        sort_column = sort_columns.get(sort_by, models.EnrolmentPricingPlan.id)
        query = query.order_by(
            sort_column.desc() if sort_order.lower() == "desc" else sort_column.asc()
        )

        return await paginate(db, query)  # pyright: ignore[reportAny]

    async def get_all_parent(
        self, db: AsyncSession, parent: Parent, owned_only: bool
    ) -> schemas.EnrolmentPricingPlanReadAllParent:
        query = select(models.EnrolmentPricingPlan).options(
            selectinload(models.EnrolmentPricingPlan.curriculum),
            selectinload(models.EnrolmentPricingPlan.branch),
            selectinload(models.EnrolmentPricingPlan.enrolments).joinedload(Enrolment.student),
        )

        if owned_only:
            student_ids = [link.student_id for link in parent.children_links]
            query = query.join(
                Enrolment,
                Enrolment.pricing_plan_id == models.EnrolmentPricingPlan.id,
            ).where(Enrolment.student_id.in_(student_ids))

        result = await db.execute(query)
        plans = result.unique().scalars().all()
        return schemas.EnrolmentPricingPlanReadAllParent(
            pricing_plans=[
                schemas.EnrolmentPricingPlanReadWithEnrolments(
                    id=plan.id,
                    curriculum_id=plan.curriculum_id,
                    curriculum_name=plan.curriculum.name,
                    branch_id=plan.branch_id,
                    branch_name=None if plan.branch_id is None else plan.branch.name,
                    name=plan.name,
                    monthly_price=plan.monthly_price,
                    start_month=plan.start_month,
                    end_month=plan.end_month,
                    enrolments=[
                        EnrolmentRead(
                            id=enrolment.id,
                            pricing_plan_id=plan.id,
                            pricing_plan_name=plan.name,
                            student_id=enrolment.student_id,
                            student_full_name=enrolment.student.full_name,
                            start_month=plan.start_month,
                            end_month=plan.end_month,
                            months_paid=enrolment.months_paid,
                        )
                        for enrolment in plan.enrolments
                    ],
                )
                for plan in plans
            ],
            children=[map_user_to_read(child.user) for child in parent.children],
        )

    async def get_by_id(self, db: AsyncSession, id: int) -> models.EnrolmentPricingPlan | None:
        query = await db.execute(
            select(models.EnrolmentPricingPlan).where(models.EnrolmentPricingPlan.id == id)
        )
        return query.scalar_one_or_none()

    async def update(
        self, db: AsyncSession, id: int, data: schemas.EnrolmentPricingPlanUpdate
    ) -> None:
        updated_values = {
            "curriculum_id": data.curriculum_id,
            "branch_id": data.branch_id,
            "name": data.name,
            "monthly_price": data.monthly_price,
            "start_month": data.start_month,
            "end_month": data.end_month,
        }
        _ = await db.execute(
            update(models.EnrolmentPricingPlan)
            .where(models.EnrolmentPricingPlan.id == id)
            .values(**updated_values)
        )

    async def delete(self, db: AsyncSession, id: int):
        _ = await db.execute(
            delete(models.EnrolmentPricingPlan).where(models.EnrolmentPricingPlan.id == id)
        )


enrolment_pricing_plan_crud = EnrolmentPricingPlanCrud()
