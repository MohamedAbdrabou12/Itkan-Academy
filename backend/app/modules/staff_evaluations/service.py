from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.staff_evaluations.crud import (
    employee_evaluation_crud,
    evaluation_comment_crud,
    evaluation_cycle_crud,
    evaluation_kpi_score_crud,
    kpi_crud,
    kpi_template_crud,
)
from app.modules.staff_evaluations.models import EvaluationStatus
from app.modules.staff_evaluations.schemas import (
    EvaluationCommentCreate,
    EvaluationCycleCreate,
    EvaluationCycleUpdate,
    KPICreate,
    KPITemplateCreate,
    KPITemplateUpdate,
    KPIUpdate,
    ScoreEvaluationRequest,
    StartEvaluationRequest,
)
from app.modules.users.models import User


class StaffEvaluationService:
    """Service for managing staff evaluations."""

    # ========== Evaluation Cycles ==========

    async def create_cycle(self, db: AsyncSession, cycle_in: EvaluationCycleCreate):
        """Create a new evaluation cycle."""
        # Check for duplicate name
        existing = await evaluation_cycle_crud.get_by_name(db, cycle_in.name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"دورة التقييم بالاسم '{cycle_in.name}' موجودة بالفعل",
            )

        # Validate dates
        if cycle_in.start_date >= cycle_in.end_date:
            raise HTTPException(
                status_code=400,
                detail="تاريخ البداية يجب أن يكون قبل تاريخ النهاية",
            )

        cycle = await evaluation_cycle_crud.create(db, cycle_in.model_dump())
        return cycle

    async def list_cycles(self, db: AsyncSession, is_active: Optional[bool] = None):
        """List evaluation cycles."""
        return await evaluation_cycle_crud.list(db, is_active)

    async def get_cycle(self, db: AsyncSession, cycle_id: int):
        """Get a specific cycle."""
        cycle = await evaluation_cycle_crud.get_by_id(db, cycle_id)
        if not cycle:
            raise HTTPException(status_code=404, detail="دورة التقييم غير موجودة")
        return cycle

    async def update_cycle(
        self, db: AsyncSession, cycle_id: int, cycle_in: EvaluationCycleUpdate
    ):
        """Update an evaluation cycle."""
        cycle = await self.get_cycle(db, cycle_id)
        update_data = cycle_in.model_dump(exclude_unset=True)

        if "start_date" in update_data or "end_date" in update_data:
            start = update_data.get("start_date", cycle.start_date)
            end = update_data.get("end_date", cycle.end_date)
            if start >= end:
                raise HTTPException(
                    status_code=400,
                    detail="تاريخ البداية يجب أن يكون قبل تاريخ النهاية",
                )

        return await evaluation_cycle_crud.update(db, cycle, update_data)

    # ========== KPI Templates ==========

    async def create_template(
        self, db: AsyncSession, template_in: KPITemplateCreate, user: User
    ):
        """Create a new KPI template with optional KPIs."""
        # Validate KPI weights if provided
        if template_in.kpis:
            total_weight = sum(kpi.weight for kpi in template_in.kpis)
            if total_weight != Decimal("100"):
                raise HTTPException(
                    status_code=400,
                    detail=f"مجموع أوزان المؤشرات يجب أن يساوي 100، حالياً: {total_weight}",
                )

        # Create template
        template_data = {
            "name": template_in.name,
            "is_global": template_in.is_global,
            "created_by_user_id": user.id,
        }
        template = await kpi_template_crud.create(db, template_data)

        # Create KPIs if provided
        if template_in.kpis:
            kpis_data = [kpi.model_dump() for kpi in template_in.kpis]
            await kpi_crud.create_bulk(db, template.id, kpis_data)

        # Reload with KPIs
        return await kpi_template_crud.get_by_id(db, template.id)

    async def list_templates(
        self,
        db: AsyncSession,
        is_global: Optional[bool] = None,
        created_by_user_id: Optional[int] = None,
    ):
        """List KPI templates."""
        return await kpi_template_crud.list(db, is_global, created_by_user_id)

    async def get_template(self, db: AsyncSession, template_id: int):
        """Get a specific template with KPIs."""
        template = await kpi_template_crud.get_by_id(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="قالب المؤشرات غير موجود")
        return template

    async def update_template(
        self, db: AsyncSession, template_id: int, template_in: KPITemplateUpdate
    ):
        """Update a KPI template."""
        template = await self.get_template(db, template_id)
        update_data = template_in.model_dump(exclude_unset=True)
        return await kpi_template_crud.update(db, template, update_data)

    async def delete_template(self, db: AsyncSession, template_id: int):
        """Delete a KPI template."""
        template = await self.get_template(db, template_id)
        # Check if template is used in any evaluations
        evaluations = await employee_evaluation_crud.list(db)
        for evaluation in evaluations:
            if evaluation.template_id == template_id:
                raise HTTPException(
                    status_code=400,
                    detail="لا يمكن حذف القالب لأنه مستخدم في تقييمات",
                )
        return await kpi_template_crud.delete(db, template_id)

    # ========== KPIs ==========

    async def add_kpi(self, db: AsyncSession, template_id: int, kpi_in: KPICreate):
        """Add a KPI to a template."""
        await self.get_template(db, template_id)

        # Check weight limit
        current_weight = await kpi_crud.get_total_weight_for_template(db, template_id)
        if current_weight + kpi_in.weight > Decimal("100"):
            raise HTTPException(
                status_code=400,
                detail=f"إضافة هذا المؤشر سيتجاوز 100%، الوزن الحالي: {current_weight}%",
            )

        kpi_data = {**kpi_in.model_dump(), "template_id": template_id}
        return await kpi_crud.create(db, kpi_data)

    async def get_kpis(self, db: AsyncSession, template_id: int):
        """Get all KPIs for a template."""
        await self.get_template(db, template_id)
        return await kpi_crud.get_by_template_id(db, template_id)

    async def update_kpi(
        self, db: AsyncSession, template_id: int, kpi_id: int, kpi_in: KPIUpdate
    ):
        """Update a KPI."""
        await self.get_template(db, template_id)
        kpi = await kpi_crud.get_by_id(db, kpi_id)
        if not kpi or kpi.template_id != template_id:
            raise HTTPException(status_code=404, detail="المؤشر غير موجود")

        # Validate weight if updating
        if kpi_in.weight is not None:
            current_weight = await kpi_crud.get_total_weight_for_template(
                db, template_id, exclude_kpi_id=kpi_id
            )
            if current_weight + kpi_in.weight > Decimal("100"):
                raise HTTPException(
                    status_code=400,
                    detail="تحديث هذا المؤشر سيتجاوز 100%",
                )

        update_data = kpi_in.model_dump(exclude_unset=True)
        return await kpi_crud.update(db, kpi, update_data)

    async def delete_kpi(self, db: AsyncSession, template_id: int, kpi_id: int):
        """Delete a KPI from a template."""
        await self.get_template(db, template_id)
        kpi = await kpi_crud.get_by_id(db, kpi_id)
        if not kpi or kpi.template_id != template_id:
            raise HTTPException(status_code=404, detail="المؤشر غير موجود")
        return await kpi_crud.delete(db, kpi_id)

    # ========== Evaluations ==========

    async def start_evaluation(
        self, db: AsyncSession, request: StartEvaluationRequest, evaluator: User
    ):
        """Start a new evaluation for an employee."""
        # Validate cycle exists and is active
        cycle = await self.get_cycle(db, request.cycle_id)
        if not cycle.is_active:
            raise HTTPException(status_code=400, detail="دورة التقييم غير نشطة")

        # Validate template exists
        template = await self.get_template(db, request.template_id)

        # Validate no duplicate evaluation for same employee in same cycle
        existing = await employee_evaluation_crud.get_by_employee_and_cycle(
            db, request.employee_user_id, request.cycle_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="يوجد تقييم بالفعل لهذا الموظف في هذه الدورة",
            )

        # Create evaluation
        evaluation_data = {
            "employee_user_id": request.employee_user_id,
            "evaluator_user_id": evaluator.id,
            "cycle_id": request.cycle_id,
            "template_id": request.template_id,
            "status": EvaluationStatus.draft,
        }
        evaluation = await employee_evaluation_crud.create(db, evaluation_data)

        # Initialize scores with 0 for all KPIs in template
        if template.kpis:
            scores_data = [
                {"kpi_id": kpi.id, "score": Decimal("0")} for kpi in template.kpis
            ]
            await evaluation_kpi_score_crud.create_bulk(db, evaluation.id, scores_data)

        return await employee_evaluation_crud.get_by_id(db, evaluation.id)

    async def get_evaluation(self, db: AsyncSession, evaluation_id: int):
        """Get an evaluation with all details."""
        evaluation = await employee_evaluation_crud.get_by_id(db, evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="التقييم غير موجود")
        return evaluation

    async def list_evaluations(
        self,
        db: AsyncSession,
        cycle_id: Optional[int] = None,
        employee_user_id: Optional[int] = None,
        evaluator_user_id: Optional[int] = None,
        status: Optional[EvaluationStatus] = None,
    ):
        """List evaluations with filters."""
        return await employee_evaluation_crud.list(
            db, cycle_id, employee_user_id, evaluator_user_id, status
        )

    async def score_evaluation(
        self, db: AsyncSession, evaluation_id: int, request: ScoreEvaluationRequest
    ):
        """Update KPI scores for an evaluation."""
        evaluation = await self.get_evaluation(db, evaluation_id)

        if evaluation.status == EvaluationStatus.approved:
            raise HTTPException(status_code=400, detail="لا يمكن تعديل تقييم معتمد")

        # Validate scores don't exceed max_score
        template = await self.get_template(db, evaluation.template_id)
        kpi_map = {kpi.id: kpi for kpi in template.kpis}

        for score in request.scores:
            if score.kpi_id not in kpi_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"المؤشر {score.kpi_id} غير موجود في القالب",
                )
            max_score = kpi_map[score.kpi_id].max_score
            if score.score > max_score:
                raise HTTPException(
                    status_code=400,
                    detail=f"الدرجة {score.score} تتجاوز الحد الأقصى {max_score}",
                )

        # Upsert scores
        scores_data = [s.model_dump() for s in request.scores]
        scores = await evaluation_kpi_score_crud.upsert_scores(
            db, evaluation_id, scores_data
        )

        return scores

    async def submit_evaluation(self, db: AsyncSession, evaluation_id: int):
        """Submit an evaluation and calculate final score."""
        evaluation = await self.get_evaluation(db, evaluation_id)

        if evaluation.status != EvaluationStatus.draft:
            raise HTTPException(
                status_code=400, detail="يمكن إرسال التقييمات المسودة فقط"
            )

        # Calculate final score
        final_score = await self._calculate_final_score(db, evaluation)

        # Update evaluation
        update_data = {
            "status": EvaluationStatus.submitted,
            "final_score": final_score,
        }
        return await employee_evaluation_crud.update(db, evaluation, update_data)

    async def approve_evaluation(self, db: AsyncSession, evaluation_id: int):
        """Approve a submitted evaluation."""
        evaluation = await self.get_evaluation(db, evaluation_id)

        if evaluation.status != EvaluationStatus.submitted:
            raise HTTPException(
                status_code=400, detail="يمكن اعتماد التقييمات المرسلة فقط"
            )

        update_data = {"status": EvaluationStatus.approved}
        return await employee_evaluation_crud.update(db, evaluation, update_data)

    async def _calculate_final_score(self, db: AsyncSession, evaluation) -> Decimal:
        """
        Calculate weighted final score.
        Formula: Final Score = Σ (KPI Score / Max Score) × KPI Weight
        """
        scores = await evaluation_kpi_score_crud.get_by_evaluation_id(db, evaluation.id)
        if not scores:
            return Decimal("0")

        template = await self.get_template(db, evaluation.template_id)
        kpi_map = {kpi.id: kpi for kpi in template.kpis}

        total_score = Decimal("0")
        for score in scores:
            kpi = kpi_map.get(score.kpi_id)
            if kpi:
                weighted = (score.score / Decimal(kpi.max_score)) * kpi.weight
                total_score += weighted

        return round(total_score, 2)

    # ========== Comments ==========

    async def add_comment(
        self, db: AsyncSession, evaluation_id: int, comment_in: EvaluationCommentCreate
    ):
        """Add a comment to an evaluation."""
        await self.get_evaluation(db, evaluation_id)
        comment_data = {
            "evaluation_id": evaluation_id,
            "comment": comment_in.comment,
        }
        return await evaluation_comment_crud.create(db, comment_data)

    async def get_comments(self, db: AsyncSession, evaluation_id: int):
        """Get all comments for an evaluation."""
        await self.get_evaluation(db, evaluation_id)
        return await evaluation_comment_crud.get_by_evaluation_id(db, evaluation_id)


# Singleton instance
staff_evaluation_service = StaffEvaluationService()
