from sqlalchemy.orm import Session


def generate_report(db: Session, report_type: str):
    if report_type == "financial":
        return {"report": "Financial report generated."}
    elif report_type == "attendance":
        return {"report": "Attendance report generated."}
    return {"report": "Unknown report type."}
