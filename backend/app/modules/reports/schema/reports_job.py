from pydantic import BaseModel
from typing import Literal


class ReportRequest(BaseModel):
    type: Literal[
        "attendance", "performance", "financial"
    ]  # restrict to specific report types
