from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.staff_evaluations.models import (
    EmployeeEvaluation,
    EvaluationComment,
    EvaluationCycle,
    EvaluationKPIScore,
    EvaluationStatus,
    KPI,
    KPITemplate,
)


class EvaluationCycleCRUD:
    async def create(self, db: AsyncSession, cycle_data: dict) -> EvaluationCycle:
        cycle = EvaluationCycle(**cycle_data)
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)
        return cycle

    async def get_by_id(
        self, db: AsyncSession, cycle_id: int
    ) -> Optional[EvaluationCycle]:
        stmt = select(EvaluationCycle).where(EvaluationCycle.id == cycle_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(
        self, db: AsyncSession, name: str
    ) -> Optional[EvaluationCycle]:
        stmt = select(EvaluationCycle).where(EvaluationCycle.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self, db: AsyncSession, is_active: Optional[bool] = None
    ) -> List[EvaluationCycle]:
        stmt = select(EvaluationCycle).order_by(EvaluationCycle.start_date.desc())
        if is_active is not None:
            stmt = stmt.where(EvaluationCycle.is_active == is_active)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, cycle: EvaluationCycle, data: dict
    ) -> EvaluationCycle:
        for field, value in data.items():
            setattr(cycle, field, value)
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)
        return cycle

    async def delete(self, db: AsyncSession, cycle_id: int) -> bool:
        cycle = await self.get_by_id(db, cycle_id)
        if cycle:
            await db.delete(cycle)
            await db.commit()
            return True
        return False


class KPITemplateCRUD:
    async def create(
        self, db: AsyncSession, template_data: dict, commit: bool = True
    ) -> KPITemplate:
        template = KPITemplate(**template_data)
        db.add(template)
        if commit:
            await db.commit()
            await db.refresh(template)
        else:
            await db.flush()
        return template

    async def get_by_id(
        self, db: AsyncSession, template_id: int
    ) -> Optional[KPITemplate]:
        stmt = (
            select(KPITemplate)
            .where(KPITemplate.id == template_id)
            .options(selectinload(KPITemplate.kpis))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        created_by_user_id: Optional[int] = None,
    ) -> List[KPITemplate]:
        stmt = select(KPITemplate).options(selectinload(KPITemplate.kpis))
        if created_by_user_id is not None:
            stmt = stmt.where(KPITemplate.created_by_user_id == created_by_user_id)
        stmt = stmt.order_by(KPITemplate.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, template: KPITemplate, data: dict, commit: bool = True
    ) -> KPITemplate:
        for field, value in data.items():
            setattr(template, field, value)
        db.add(template)
        if commit:
            await db.commit()
            await db.refresh(template)
        else:
            await db.flush()
        return template

    async def delete(self, db: AsyncSession, template_id: int) -> bool:
        template = await self.get_by_id(db, template_id)
        if template:
            await db.delete(template)
            await db.commit()
            return True
        return False


class KPICRUD:
    async def create(
        self, db: AsyncSession, kpi_data: dict, commit: bool = True
    ) -> KPI:
        kpi = KPI(**kpi_data)
        db.add(kpi)
        if commit:
            await db.commit()
            await db.refresh(kpi)
        else:
            await db.flush()
        return kpi

    async def create_bulk(
        self, db: AsyncSession, template_id: int, kpis: List[dict], commit: bool = True
    ) -> List[KPI]:
        new_kpis = [KPI(template_id=template_id, **kpi) for kpi in kpis]
        db.add_all(new_kpis)
        if commit:
            await db.commit()
            for kpi in new_kpis:
                await db.refresh(kpi)
        else:
            await db.flush()
        return new_kpis

    async def get_by_id(self, db: AsyncSession, kpi_id: int) -> Optional[KPI]:
        stmt = select(KPI).where(KPI.id == kpi_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_template_id(self, db: AsyncSession, template_id: int) -> List[KPI]:
        stmt = select(KPI).where(KPI.template_id == template_id).order_by(KPI.id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_total_weight_for_template(
        self, db: AsyncSession, template_id: int, exclude_kpi_id: Optional[int] = None
    ) -> Decimal:
        kpis = await self.get_by_template_id(db, template_id)
        total = Decimal("0")
        for kpi in kpis:
            if exclude_kpi_id and kpi.id == exclude_kpi_id:
                continue
            total += kpi.weight
        return total

    async def update(
        self, db: AsyncSession, kpi: KPI, data: dict, commit: bool = True
    ) -> KPI:
        for field, value in data.items():
            setattr(kpi, field, value)
        db.add(kpi)
        if commit:
            await db.commit()
            await db.refresh(kpi)
        else:
            await db.flush()
        return kpi

    async def delete(self, db: AsyncSession, kpi_id: int, commit: bool = True) -> bool:
        kpi = await self.get_by_id(db, kpi_id)
        if kpi:
            await db.delete(kpi)
            if commit:
                await db.commit()
            else:
                await db.flush()
            return True
        return False


class EmployeeEvaluationCRUD:
    async def create(
        self, db: AsyncSession, evaluation_data: dict
    ) -> EmployeeEvaluation:
        evaluation = EmployeeEvaluation(**evaluation_data)
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    async def get_by_id(
        self, db: AsyncSession, evaluation_id: int
    ) -> Optional[EmployeeEvaluation]:
        stmt = (
            select(EmployeeEvaluation)
            .where(EmployeeEvaluation.id == evaluation_id)
            .options(
                selectinload(EmployeeEvaluation.kpi_scores).joinedload(
                    EvaluationKPIScore.kpi
                ),
                selectinload(EmployeeEvaluation.comments),
                joinedload(EmployeeEvaluation.cycle),
                joinedload(EmployeeEvaluation.template).selectinload(KPITemplate.kpis),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_employee_and_cycle(
        self, db: AsyncSession, employee_user_id: int, cycle_id: int, branch_id: int
    ) -> Optional[EmployeeEvaluation]:
        stmt = select(EmployeeEvaluation).where(
            and_(
                EmployeeEvaluation.employee_user_id == employee_user_id,
                EmployeeEvaluation.cycle_id == cycle_id,
                EmployeeEvaluation.branch_id == branch_id,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        cycle_id: Optional[int] = None,
        employee_user_id: Optional[int] = None,
        evaluator_user_id: Optional[int] = None,
        status: Optional[EvaluationStatus] = None,
        branch_id: Optional[int] = None,
    ) -> List[EmployeeEvaluation]:
        stmt = select(EmployeeEvaluation).options(
            joinedload(EmployeeEvaluation.cycle),
            joinedload(EmployeeEvaluation.template),
            joinedload(EmployeeEvaluation.employee),
            joinedload(EmployeeEvaluation.evaluator),
        )
        if cycle_id is not None:
            stmt = stmt.where(EmployeeEvaluation.cycle_id == cycle_id)
        if employee_user_id is not None:
            stmt = stmt.where(EmployeeEvaluation.employee_user_id == employee_user_id)
        if evaluator_user_id is not None:
            stmt = stmt.where(EmployeeEvaluation.evaluator_user_id == evaluator_user_id)
        if status is not None:
            stmt = stmt.where(EmployeeEvaluation.status == status)
        if branch_id is not None:
            stmt = stmt.where(EmployeeEvaluation.branch_id == branch_id)
        stmt = stmt.order_by(EmployeeEvaluation.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, evaluation: EmployeeEvaluation, data: dict
    ) -> EmployeeEvaluation:
        for field, value in data.items():
            setattr(evaluation, field, value)
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    async def delete(self, db: AsyncSession, evaluation_id: int) -> bool:
        evaluation = await self.get_by_id(db, evaluation_id)
        if evaluation:
            await db.delete(evaluation)
            await db.commit()
            return True
        return False


class EvaluationKPIScoreCRUD:
    async def create(self, db: AsyncSession, score_data: dict) -> EvaluationKPIScore:
        score = EvaluationKPIScore(**score_data)
        db.add(score)
        await db.commit()
        await db.refresh(score)
        return score

    async def create_bulk(
        self, db: AsyncSession, evaluation_id: int, scores: List[dict]
    ) -> List[EvaluationKPIScore]:
        new_scores = [
            EvaluationKPIScore(evaluation_id=evaluation_id, **score) for score in scores
        ]
        db.add_all(new_scores)
        await db.commit()
        for score in new_scores:
            await db.refresh(score)
        return new_scores

    async def get_by_evaluation_id(
        self, db: AsyncSession, evaluation_id: int
    ) -> List[EvaluationKPIScore]:
        stmt = (
            select(EvaluationKPIScore)
            .where(EvaluationKPIScore.evaluation_id == evaluation_id)
            .options(joinedload(EvaluationKPIScore.kpi))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_evaluation_and_kpi(
        self, db: AsyncSession, evaluation_id: int, kpi_id: int
    ) -> Optional[EvaluationKPIScore]:
        stmt = select(EvaluationKPIScore).where(
            and_(
                EvaluationKPIScore.evaluation_id == evaluation_id,
                EvaluationKPIScore.kpi_id == kpi_id,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_scores(
        self, db: AsyncSession, evaluation_id: int, scores: List[dict]
    ) -> List[EvaluationKPIScore]:
        """Create or update scores for an evaluation."""
        result_scores = []
        for score_data in scores:
            existing = await self.get_by_evaluation_and_kpi(
                db, evaluation_id, score_data["kpi_id"]
            )
            if existing:
                existing.score = score_data["score"]
                db.add(existing)
                result_scores.append(existing)
            else:
                new_score = EvaluationKPIScore(
                    evaluation_id=evaluation_id, **score_data
                )
                db.add(new_score)
                result_scores.append(new_score)
        await db.commit()
        for score in result_scores:
            await db.refresh(score)
        return result_scores


class EvaluationCommentCRUD:
    async def create(self, db: AsyncSession, comment_data: dict) -> EvaluationComment:
        comment = EvaluationComment(**comment_data)
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    async def get_by_evaluation_id(
        self, db: AsyncSession, evaluation_id: int
    ) -> List[EvaluationComment]:
        stmt = (
            select(EvaluationComment)
            .where(EvaluationComment.evaluation_id == evaluation_id)
            .order_by(EvaluationComment.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, db: AsyncSession, comment_id: int) -> bool:
        stmt = select(EvaluationComment).where(EvaluationComment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()
        if comment:
            await db.delete(comment)
            await db.commit()
            return True
        return False


# Singleton instances
evaluation_cycle_crud = EvaluationCycleCRUD()
kpi_template_crud = KPITemplateCRUD()
kpi_crud = KPICRUD()
employee_evaluation_crud = EmployeeEvaluationCRUD()
evaluation_kpi_score_crud = EvaluationKPIScoreCRUD()
evaluation_comment_crud = EvaluationCommentCRUD()
