from sqlalchemy.orm import Session
from app.modules.branches import models, schemas


def create_branch(db: Session, branch_in: schemas.BranchCreate):
    branch = models.Branch(**branch_in.dict())
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


def get_branches(db: Session):
    return db.query(models.Branch).all()
