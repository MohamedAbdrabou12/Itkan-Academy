from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.authorization import require_permission
from app.modules.permissions.permissions import PermissionCode
from app.modules.reports.schemas.base import ExportType
from app.modules.reports.utils.export import export_csv, export_excel, export_pdf
from app.modules.reports.crud.employees import (
    query_teacher_attendance_data,
    query_staff_attendance_data,
    get_latest_evaluation_scores,
)
from app.modules.reports.models.employees import TeacherReportData, EmployeeReportData

employee_reports_router = APIRouter()

@employee_reports_router.get(
    "/teachers",
    dependencies=[Depends(require_permission(PermissionCode.REPORTS_TEACHERS_VIEW))],
)
async def generate_teachers_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query(alias="branch_ids")] = None,
    class_ids: Annotated[List[int] | None, Query(alias="class_ids")] = None,
    teacher_ids: Annotated[List[int] | None, Query(alias="teacher_ids")] = None,
    export_type: Annotated[ExportType | None, Query()] = None,
):
    attendance_records = await query_teacher_attendance_data(
        db=db,
        date_from=date_from,
        date_to=date_to,
        branch_ids=branch_ids,
        class_ids=class_ids,
        teacher_ids=teacher_ids,
    )

    user_ids = list({rec.user_id for rec in attendance_records})
    latest_evals = await get_latest_evaluation_scores(db, user_ids)

    report_data = []
    for rec in attendance_records:
        eval_rec = latest_evals.get(rec.user_id)
        class_names = ", ".join([c.name for c in rec.user.teacher.classes]) if rec.user.teacher and rec.user.teacher.classes else ""
        
        report_data.append(
            TeacherReportData(
                branch_id=rec.branch_id,
                branch_name=rec.branch.name,
                employee_id=rec.user_id,
                employee_name=rec.user.full_name,
                role_name=rec.user.role.name_ar if rec.user.role else "معلم",
                date=rec.date.isoformat(),
                status=rec.status,
                check_in=rec.check_in_time.strftime("%H:%M") if rec.check_in_time else None,
                check_out=rec.check_out_time.strftime("%H:%M") if rec.check_out_time else None,
                worked_minutes=rec.worked_minutes,
                evaluation_score=float(eval_rec.final_score) if eval_rec and eval_rec.final_score is not None else None,
                evaluator_name=eval_rec.evaluator.full_name if eval_rec and eval_rec.evaluator else None,
                classes=class_names,
            )
        )

    if export_type:
        report_dicts = [item.model_dump(mode="json") for item in report_data]
        if export_type == ExportType.PDF:
            return export_pdf(
                report_data=report_dicts,
                file_name="teachers_report",
                date_from=date_from,
                date_to=date_to,
                title="تقرير المعلمين",
            )
        elif export_type == ExportType.CSV:
            return export_csv(
                report_data=report_dicts,
                file_name="teachers_report",
                date_from=date_from,
                date_to=date_to,
            )
        elif export_type == ExportType.EXCEL:
            return export_excel(
                report_data=report_dicts,
                file_name="teachers_report",
                date_from=date_from,
                date_to=date_to,
            )

    return report_data

@employee_reports_router.get(
    "/staff",
    dependencies=[Depends(require_permission(PermissionCode.REPORTS_STAFF_VIEW))],
)
async def generate_staff_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query(alias="branch_ids")] = None,
    staff_ids: Annotated[List[int] | None, Query(alias="staff_ids")] = None,
    export_type: Annotated[ExportType | None, Query()] = None,
):
    attendance_records = await query_staff_attendance_data(
        db=db,
        date_from=date_from,
        date_to=date_to,
        branch_ids=branch_ids,
        staff_ids=staff_ids,
    )

    user_ids = list({rec.user_id for rec in attendance_records})
    latest_evals = await get_latest_evaluation_scores(db, user_ids)

    report_data = []
    for rec in attendance_records:
        eval_rec = latest_evals.get(rec.user_id)
        
        report_data.append(
            EmployeeReportData(
                branch_id=rec.branch_id,
                branch_name=rec.branch.name,
                employee_id=rec.user_id,
                employee_name=rec.user.full_name,
                role_name=rec.user.role.name_ar if rec.user.role else "موظف",
                date=rec.date.isoformat(),
                status=rec.status,
                check_in=rec.check_in_time.strftime("%H:%M") if rec.check_in_time else None,
                check_out=rec.check_out_time.strftime("%H:%M") if rec.check_out_time else None,
                worked_minutes=rec.worked_minutes,
                evaluation_score=float(eval_rec.final_score) if eval_rec and eval_rec.final_score is not None else None,
                evaluator_name=eval_rec.evaluator.full_name if eval_rec and eval_rec.evaluator else None,
            )
        )

    if export_type:
        report_dicts = [item.model_dump(mode="json") for item in report_data]
        if export_type == ExportType.PDF:
            return export_pdf(
                report_data=report_dicts,
                file_name="staff_report",
                date_from=date_from,
                date_to=date_to,
                title="تقرير الموظفين",
            )
        elif export_type == ExportType.CSV:
            return export_csv(
                report_data=report_dicts,
                file_name="staff_report",
                date_from=date_from,
                date_to=date_to,
            )
        elif export_type == ExportType.EXCEL:
            return export_excel(
                report_data=report_dicts,
                file_name="staff_report",
                date_from=date_from,
                date_to=date_to,
            )

    return report_data
