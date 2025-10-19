from sqlalchemy.orm import Session
from app.modules.financial import models, schemas


def create_transaction(db: Session, txn_in: schemas.TransactionCreate):
    txn = models.Transaction(**txn_in.dict())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def get_transactions(db: Session):
    return db.query(models.Transaction).all()
