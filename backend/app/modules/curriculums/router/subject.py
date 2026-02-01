from typing import Annotated

from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.curriculums.crud.subject import subject_crud
from app.modules.curriculums.schemas.subject import (
    DetailedSubjectResponse,
    SubjectCreate,
    SubjectResponse,
    SubjectUpdate,
)
from app.modules.curriculums.schemas.unit import DetailedUnitResponse
from app.modules.curriculums.schemas.unit_item import UnitItemResponse
from app.modules.permissions.permissions import PermissionCode
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

subjects_router = APIRouter(prefix="/subjects")


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
async def get_subjects(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SubjectResponse]:
    subjects = await subject_crud.get_all(db)
    return [SubjectResponse(id=subject.id, name=subject.name) for subject in subjects]


@subjects_router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_VIEW))],
)
async def get(db: Annotated[AsyncSession, Depends(get_db)], id: int) -> DetailedSubjectResponse:
    subject = await subject_crud.get(db, id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject {id} not found")

    return DetailedSubjectResponse(
        id=subject.id,
        name=subject.name,
        units=sorted(
            [
                DetailedUnitResponse(
                    id=unit.id,
                    title=unit.title,
                    description=unit.description,
                    subject_id=unit.subject_id,
                    curriculum_id=unit.curriculum_id,
                    curriculum_name=unit.curriculum.name,
                    subject_name=unit.subject.name,
                    items=sorted(
                        [
                            UnitItemResponse(
                                id=item.id,
                                title=item.title,
                                type=item.type,
                                content=item.content,
                                unit_id=item.unit_id,
                            )
                            for item in unit.items
                        ],
                        key=lambda resp: resp.id,
                    ),
                )
                for unit in subject.units
            ],
            key=lambda resp: resp.curriculum_id,
        ),
    )


@subjects_router.get(
    "/by-curriculum/{curriculum_id}",
    status_code=status.HTTP_200_OK,
)
async def get_by_curriculum(
    db: Annotated[AsyncSession, Depends(get_db)], curriculum_id: int
) -> list[SubjectResponse]:
    subjects = await subject_crud.get_by_curriculum(db, curriculum_id)
    return [SubjectResponse(id=subject.id, name=subject.name) for subject in subjects]


@subjects_router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ACADEMIC_EDUCATIONAL_CONTENT_EDIT))],
)
async def edit_subject(
    db: Annotated[AsyncSession, Depends(get_db)], id: int, data: SubjectUpdate
) -> None:
    await subject_crud.update(db, id, data)
