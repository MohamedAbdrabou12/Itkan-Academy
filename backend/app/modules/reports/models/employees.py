from typing import Optional
from pydantic import BaseModel, field_serializer
from app.modules.attendance.models import AttendanceStatus

class EmployeeReportData(BaseModel):
    branch_id: int
    branch_name: str
    employee_id: int
    employee_name: str
    role_name: str
    date: str
    status: AttendanceStatus
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    worked_minutes: Optional[int] = None
    evaluation_score: Optional[float] = None
    evaluator_name: Optional[str] = None

    @field_serializer("status")
    def serialize_status(self, status: AttendanceStatus) -> str:
        arabic_mapping = {
            AttendanceStatus.present: "حاضر",
            AttendanceStatus.absent: "غائب",
            AttendanceStatus.late: "متأخر",
            AttendanceStatus.half_day: "نصف يوم",
            AttendanceStatus.on_leave: "في إجازة",
        }
        return arabic_mapping.get(status, str(status))

class TeacherReportData(EmployeeReportData):
    classes: Optional[str] = None
