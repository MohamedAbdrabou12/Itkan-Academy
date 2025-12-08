from datetime import date

from pydantic import BaseModel

# WARNING: The base classes should not be used on their own.
# Their purpose is to extend other schemas. Use any of the other schema files or make your own.


class ReportGenerateBase(BaseModel):
    start_date: date
    end_date: date
