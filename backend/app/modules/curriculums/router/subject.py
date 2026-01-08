from typing import Annotated

from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.curriculums.crud.subject import subject_crud
from app.modules.curriculums.models.curriculum import CurriculumSubject
from app.modules.curriculums.router.unit import units_router
from app.modules.curriculums.schemas.curriculum import CurriculumResponse
from app.modules.curriculums.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from app.modules.curriculums.schemas.unit import UnitResponse
from app.modules.permissions.permissions import PermissionCode
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

subjects_router = APIRouter(prefix="/subjects")

subjects_router.include_router(units_router)


@subjects_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_ADD))],
)
async def create_subject(
    db: Annotated[AsyncSession, Depends(get_db)], data: SubjectCreate
) -> SubjectResponse:
    subject = await subject_crud.create(db, data)
    return SubjectResponse(id=subject.id, name=subject.name)


@subjects_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_VIEW))],
)
async def get_subjects(db: Annotated[AsyncSession, Depends(get_db)]) -> list[SubjectResponse]:
    subjects = await subject_crud.get_all(db)
    return [SubjectResponse(id=subject.id, name=subject.name) for subject in subjects]


@subjects_router.get(
    "/{id}/curriculums",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_CURRICULUM_VIEW))],
)
async def get_curriculums(
    db: Annotated[AsyncSession, Depends(get_db)], id: int
) -> list[CurriculumResponse]:
    curriculums = await subject_crud.get_curriculums(db, id)
    if curriculums is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject with ID {id} not found"
        )

    return [
        CurriculumResponse(
            id=curriculum.id,
            name=curriculum.name,
            description=curriculum.description,
            academic_year=curriculum.academic_year,
            is_active=curriculum.is_active,
        )
        for curriculum in curriculums
    ]


@subjects_router.get(
    "/{id}/units",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_VIEW))],
)
async def get_units(
    db: Annotated[AsyncSession, Depends(get_db)], id: int
) -> list[UnitResponse]:
    units = await subject_crud.get_units(db, id)
    if units is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject {id} not found")

    return [
        UnitResponse(
            id=unit.id, title=unit.title, description=unit.description, subject_id=unit.subject_id
        )
        for unit in units
    ]


@subjects_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_VIEW))],
)
async def edit_subject(
    db: Annotated[AsyncSession, Depends(get_db)], id: int, data: SubjectUpdate
) -> None:
    await subject_crud.update(db, id, data)


@subjects_router.put(
    "/{id}/assign_to_curriculum/{curr_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_EDIT))],
)
async def assign_to_curriculum(
    db: Annotated[AsyncSession, Depends(get_db)], id: int, curr_id: int
) -> None:
    await db.merge(CurriculumSubject(subject_id=id, curriculum_id=curr_id))
    await db.commit()
