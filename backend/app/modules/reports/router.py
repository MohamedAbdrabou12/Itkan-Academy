from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db
from app.modules.reports import crud, schemas

router = APIRouter()


@router.post("/")
def generate_report(request: schemas.ReportRequest, db: Session = Depends(get_db)):
    return crud.generate_report(db, request.type)
