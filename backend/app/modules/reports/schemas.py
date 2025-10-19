from pydantic import BaseModel


class ReportRequest(BaseModel):
    type: str  # 'attendance', 'performance', 'financial'
