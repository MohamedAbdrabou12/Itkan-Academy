from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.authorization import require_permission
from app.modules.permissions.permissions import PermissionCode
from app.modules.reports.schemas.base import ExportType
from app.modules.reports.utils.export import export_csv, export_excel, export_pdf
from app.modules.reports.crud.financial import (
    query_revenue_by_branch,
    query_outstanding_tuition,
    query_teacher_payroll,
    query_student_payments,
)
from app.modules.reports.models.financial import (
    RevenueByBranchReportData,
    OutstandingTuitionReportData,
    TeacherPayrollReportData,
    StudentPaymentReportData,
)

financial_reports_router = APIRouter(prefix="/finance", tags=["Financial Reports"])

@financial_reports_router.get(
    "/revenue-by-branch",
    response_model=List[RevenueByBranchReportData],
    dependencies=[Depends(require_permission(PermissionCode.REPORTS_FINANCE_VIEW))],
)
async def get_revenue_by_branch_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query(alias="branch_ids")] = None,
    export_type: Annotated[ExportType | None, Query()] = None,
):
    data = await query_revenue_by_branch(
        db=db,
        date_from=date_from,
        date_to=date_to,
        branch_ids=branch_ids,
    )
    
    report_data = [RevenueByBranchReportData(**item) for item in data]
    
    if export_type:
        report_dicts = [item.model_dump(mode="json") for item in report_data]
        if export_type == ExportType.PDF:
            return export_pdf(
                report_data=report_dicts,
                file_name="revenue_by_branch_report",
                date_from=date_from,
                date_to=date_to,
                title="تقرير الإيرادات حسب الفروع",
            )
        elif export_type == ExportType.CSV:
            return export_csv(
                report_data=report_dicts,
                file_name="revenue_by_branch_report",
                date_from=date_from,
                date_to=date_to,
            )
        elif export_type == ExportType.EXCEL:
            return export_excel(
                report_data=report_dicts,
                file_name="revenue_by_branch_report",
                date_from=date_from,
                date_to=date_to,
            )
            
    return report_data

@financial_reports_router.get(
    "/outstanding-tuition",
    response_model=List[OutstandingTuitionReportData],
    dependencies=[Depends(require_permission(PermissionCode.REPORTS_FINANCE_VIEW))],
)
async def get_outstanding_tuition_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query(alias="branch_ids")] = None,
    student_ids: Annotated[List[int] | None, Query(alias="student_ids")] = None,
    export_type: Annotated[ExportType | None, Query()] = None,
):
    invoices = await query_outstanding_tuition(
        db=db,
        date_from=date_from,
        date_to=date_to,
        branch_ids=branch_ids,
        student_ids=student_ids,
    )
    
    report_data = []
    for inv in invoices:
        branch_name = inv.student.user.branches[0].name if inv.student.user.branches else "غير محدد"
        branch_id = inv.student.user.branches[0].id if inv.student.user.branches else 0
        
        report_data.append(
            OutstandingTuitionReportData(
                invoice_id=inv.id,
                branch_id=branch_id,
                branch_name=branch_name,
                student_id=inv.student_id,
                student_name=inv.student.user.full_name,
                amount=float(inv.amount),
                due_date=inv.due_date.isoformat(),
                status=inv.status,
                description=inv.description,
            )
        )
        
    if export_type:
        report_dicts = [item.model_dump(mode="json") for item in report_data]
        if export_type == ExportType.PDF:
            return export_pdf(
                report_data=report_dicts,
                file_name="outstanding_tuition_report",
                date_from=date_from,
                date_to=date_to,
                title="تقرير الرسوم الدراسية المستحقة",
            )
        elif export_type == ExportType.CSV:
            return export_csv(
                report_data=report_dicts,
                file_name="outstanding_tuition_report",
                date_from=date_from,
                date_to=date_to,
            )
        elif export_type == ExportType.EXCEL:
            return export_excel(
                report_data=report_dicts,
                file_name="outstanding_tuition_report",
                date_from=date_from,
                date_to=date_to,
            )
            
    return report_data

@financial_reports_router.get(
    "/teacher-payroll",
    response_model=List[TeacherPayrollReportData],
    dependencies=[Depends(require_permission(PermissionCode.REPORTS_FINANCE_VIEW))],
)
async def get_teacher_payroll_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query(alias="branch_ids")] = None,
    teacher_ids: Annotated[List[int] | None, Query(alias="teacher_ids")] = None,
    export_type: Annotated[ExportType | None, Query()] = None,
):
    records = await query_teacher_payroll(
        db=db,
        date_from=date_from,
        date_to=date_to,
        branch_ids=branch_ids,
        teacher_ids=teacher_ids,
    )
    
    report_data = []
    for rec in records:
        branch_names = ", ".join([b.name for b in rec.employee.branches]) if rec.employee.branches else "غير محدد"
        net_salary = float(rec.base_salary + rec.allowance + rec.bonuses - rec.deductions)
        
        report_data.append(
            TeacherPayrollReportData(
                record_id=rec.id,
                cycle_id=rec.cycle_id,
                cycle_name=f"{rec.cycle.month}/{rec.cycle.year}",
                employee_id=rec.employee_id,
                employee_name=rec.employee.full_name,
                branch_names=branch_names,
                base_salary=float(rec.base_salary),
                allowance=float(rec.allowance),
                bonuses=float(rec.bonuses),
                deductions=float(rec.deductions),
                net_salary=net_salary,
            )
        )
        
    if export_type:
        report_dicts = [item.model_dump(mode="json") for item in report_data]
        if export_type == ExportType.PDF:
            return export_pdf(
                report_data=report_dicts,
                file_name="teacher_payroll_report",
                date_from=date_from,
                date_to=date_to,
                title="تقرير رواتب المعلمين",
            )
        elif export_type == ExportType.CSV:
            return export_csv(
                report_data=report_dicts,
                file_name="teacher_payroll_report",
                date_from=date_from,
                date_to=date_to,
            )
        elif export_type == ExportType.EXCEL:
            return export_excel(
                report_data=report_dicts,
                file_name="teacher_payroll_report",
                date_from=date_from,
                date_to=date_to,
            )
            
    return report_data

@financial_reports_router.get(
    "/student-payments",
    response_model=List[StudentPaymentReportData],
    dependencies=[Depends(require_permission(PermissionCode.REPORTS_FINANCE_VIEW))],
)
async def get_student_payments_report(
    date_from: Annotated[str, Query(alias="from")],
    date_to: Annotated[str, Query(alias="to")],
    db: AsyncSession = Depends(get_db),
    branch_ids: Annotated[List[int] | None, Query(alias="branch_ids")] = None,
    student_ids: Annotated[List[int] | None, Query(alias="student_ids")] = None,
    export_type: Annotated[ExportType | None, Query()] = None,
):
    payments = await query_student_payments(
        db=db,
        date_from=date_from,
        date_to=date_to,
        branch_ids=branch_ids,
        student_ids=student_ids,
    )
    
    report_data = []
    for p in payments:
        branch_name = p.invoice.student.user.branches[0].name if p.invoice.student.user.branches else "غير محدد"
        
        report_data.append(
            StudentPaymentReportData(
                payment_id=p.id,
                invoice_id=p.invoice_id,
                student_id=p.invoice.student_id,
                student_name=p.invoice.student.user.full_name,
                branch_name=branch_name,
                amount=float(p.amount) if p.amount is not None else 0.0,
                status=p.status,
                gateway=p.gateway,
                external_txn_id=p.external_txn_id,
                paid_at=p.paid_at.isoformat() if p.paid_at else None,
            )
        )
        
    if export_type:
        report_dicts = [item.model_dump(mode="json") for item in report_data]
        if export_type == ExportType.PDF:
            return export_pdf(
                report_data=report_dicts,
                file_name="student_payments_report",
                date_from=date_from,
                date_to=date_to,
                title="سجل مدفوعات الطلاب",
            )
        elif export_type == ExportType.CSV:
            return export_csv(
                report_data=report_dicts,
                file_name="student_payments_report",
                date_from=date_from,
                date_to=date_to,
            )
        elif export_type == ExportType.EXCEL:
            return export_excel(
                report_data=report_dicts,
                file_name="student_payments_report",
                date_from=date_from,
                date_to=date_to,
            )
            
    return report_data
