from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db
from app.modules.branches import crud, schemas

router = APIRouter()


@router.post("/", response_model=schemas.BranchOut)
def create_branch(branch_in: schemas.BranchCreate, db: Session = Depends(get_db)):
    return crud.create_branch(db, branch_in)


@router.get("/", response_model=list[schemas.BranchOut])
def list_branches(db: Session = Depends(get_db)):
    return crud.get_branches(db)
