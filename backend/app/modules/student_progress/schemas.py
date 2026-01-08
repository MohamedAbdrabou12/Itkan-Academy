from datetime import datetime

from pydantic import BaseModel


class StudentProgressResponse(BaseModel):
    id: int
    student_id: int
    unit_item_id: int
    evaluation_id: int | None
    exam_attempt_id: int | None
    created_at: datetime
