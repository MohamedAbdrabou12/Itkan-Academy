from typing import List, Optional

from app.modules.reports.schemas.base import ReportGenerateBase


class StudentReportGenerate(ReportGenerateBase):
    branch_ids: Optional[List[int]]
    class_ids: Optional[List[int]]
    student_id: Optional[List[int]]
