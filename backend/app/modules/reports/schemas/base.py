from datetime import date
from enum import Enum

from pydantic import BaseModel

# WARNING: The base classes should not be used on their own.
# Their purpose is to extend other schemas. Use any of the other schema files or make your own.


class ReportGenerateBase(BaseModel):
    start_date: date
    end_date: date


class ExportType(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
