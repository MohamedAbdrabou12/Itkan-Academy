from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db
from app.modules.financial import crud, schemas

router = APIRouter()


@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(
    txn_in: schemas.TransactionCreate, db: Session = Depends(get_db)
):
    return crud.create_transaction(db, txn_in)


@router.get("/", response_model=list[schemas.TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    return crud.get_transactions(db)
