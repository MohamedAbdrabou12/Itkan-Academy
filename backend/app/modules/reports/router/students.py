from typing import Annotated, List

from app.db.session import get_db
from app.modules.evaluations.models import AttendanceStatus
from app.modules.reports.crud.students import query_evaluation_data
from app.modules.reports.models.students import (
    StudentAttendanceReportData,
    StudentEvaluationReportData,
)
from app.modules.reports.schemas.base import ExportType
from app.modules.reports.utils.export import export_csv_or_excel_file
from app.modules.reports.utils.flatten_data import (
    flatten_evaluation_data_for_export,
)
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

student_reports_router = APIRouter(prefix="/students")


@student_reports_router.get("/attendance")
async def generate_attendance_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query()] = None,
    class_ids: Annotated[List[int] | None, Query()] = None,
    student_ids: Annotated[List[int] | None, Query()] = None,
    attendance_status: Annotated[List[AttendanceStatus] | None, Query()] = None,
    export_type: Annotated[ExportType | None, Query()] = None,
):
    evaluations = await query_evaluation_data(
        db, date_from, date_to, branch_ids, class_ids, student_ids, attendance_status
    )

    # Prepare the data using your Pydantic model
    report_data = [
        StudentAttendanceReportData(
            branch_id=evaluation.branch_id,
            branch_name=evaluation.branch.name,
            class_id=evaluation.class_id,
            class_name=evaluation.class_.name,
            student_id=evaluation.student_id,
            student_name=evaluation.student.user.full_name,
            date=evaluation.date.isoformat(),
            status=evaluation.attendance_status,
        )
        for evaluation in evaluations
    ]

    if export_type:
        if export_type == ExportType.PDF:
            pass
        elif export_type == ExportType.CSV:
            return export_csv_or_excel_file(
                report_data=report_data,
                file_name="attendance",
                date_from=date_from,
                date_to=date_to,
                export_format="csv",
            )
        elif export_type == ExportType.EXCEL:
            return export_csv_or_excel_file(
                report_data=report_data,
                file_name="attendance",
                date_from=date_from,
                date_to=date_to,
                export_format="excel",
            )

    return report_data


@student_reports_router.get("/evaluations")
async def generate_evaluations_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query()] = None,
    class_ids: Annotated[List[int] | None, Query()] = None,
    student_ids: Annotated[List[int] | None, Query()] = None,
    export_type: Annotated[ExportType | None, Query()] = None,
):
    evaluations = await query_evaluation_data(
        db, date_from, date_to, branch_ids, class_ids, student_ids
    )

    report_data = [
        StudentEvaluationReportData(
            branch_id=evaluation.branch_id,
            branch_name=evaluation.branch.name,
            class_id=evaluation.class_id,
            class_name=evaluation.class_.name,
            student_id=evaluation.student_id,
            student_name=evaluation.student.user.full_name,
            date=evaluation.date.isoformat(),
            evaluation_grades=evaluation.evaluation_grades,
        )
        for evaluation in evaluations
    ]

    if export_type:
        # Convert to dictionaries
        data_dicts = [item.model_dump() for item in report_data]

        # Prepare flattened data for export (one row per evaluation)
        export_rows = []
        for item in data_dicts:
            grades = item.get("evaluation_grades", [])

            if grades:
                # One row per evaluation grade
                for grade in grades:
                    export_rows.append(
                        {
                            "branch_id": item["branch_id"],
                            "branch_name": item["branch_name"],
                            "class_id": item["class_id"],
                            "class_name": item["class_name"],
                            "student_id": item["student_id"],
                            "student_name": item["student_name"],
                            "date": item["date"],
                            "evaluation_name": grade.get("name", ""),
                            "grade": grade.get("grade", ""),
                        }
                    )
            else:
                # Empty row if no grades
                export_rows.append(
                    {
                        "branch_id": item["branch_id"],
                        "branch_name": item["branch_name"],
                        "class_id": item["class_id"],
                        "class_name": item["class_name"],
                        "student_id": item["student_id"],
                        "student_name": item["student_name"],
                        "date": item["date"],
                        "evaluation_name": "",
                        "grade": "",
                    }
                )

        # Pivot the data
        pivoted_data = flatten_evaluation_data_for_export(export_rows)

        if export_type == ExportType.PDF:
            pass
        elif export_type == ExportType.CSV:
            return export_csv_or_excel_file(
                report_data=pivoted_data,
                file_name="evaluations",
                date_from=date_from,
                date_to=date_to,
                export_format="csv",
            )
        elif export_type == ExportType.EXCEL:
            return export_csv_or_excel_file(
                report_data=pivoted_data,
                file_name="evaluations",
                date_from=date_from,
                date_to=date_to,
                export_format="excel",
            )

    return report_data
