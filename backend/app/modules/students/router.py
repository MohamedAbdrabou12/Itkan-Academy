from typing import Dict, List, Optional

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.permissions.permissions import PermissionCode
from app.modules.students.schemas import StudentCreate, StudentRead, StudentUpdate
from app.modules.students.service import StudentService
from app.modules.users.models import User
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

students_router = APIRouter(prefix="/students", tags=["Students"])


@students_router.get(
    "/",
    response_model=dict,
    dependencies=[Depends(require_permission(PermissionCode.SYSTEM_STUDENTS_VIEW))],
)
async def list_students(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    search: Optional[str] = Query(
        None, description="Search by name, email or national_id"
    ),
    sort_by: Optional[str] = Query(
        None,
        description="Sort by: full_name, email, status, national_id, admission_date, curriculum_progress",
    ),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
    status: Optional[str] = Query(None, description="Filter by user status"),
):
    students_page = await StudentService.list_students(
        db,
        page=page,
        size=size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        status=status,
    )

    return {
        "items": students_page["items"],
        "page": students_page["page"],
        "size": students_page["size"],
        "total": students_page["total"],
        "pages": students_page["pages"],
    }


@students_router.post("/by-classes", response_model=List[Dict])
async def get_students_by_classes(
    db: AsyncSession = Depends(get_db),
    class_ids: List[int] = Body(..., embed=True),
):
    students = await StudentService.get_students_by_classes(db, class_ids)
    if not students:
        raise HTTPException(
            status_code=404, detail="No students found for these branches"
        )
    return students


@students_router.get(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[Depends(require_permission(PermissionCode.SYSTEM_STUDENTS_VIEW))],
)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    return await StudentService.get_student(db, student_id)


@students_router.post(
    "/",
    response_model=StudentRead,
    status_code=201,
    dependencies=[Depends(require_permission(PermissionCode.SYSTEM_STUDENTS_ADD))],
)
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StudentService.create_student(db, student_in, current_user)


@students_router.put(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[Depends(require_permission(PermissionCode.SYSTEM_STUDENTS_EDIT))],
)
async def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await StudentService.update_student(db, student_id, student_in)


@students_router.delete(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[Depends(require_permission(PermissionCode.SYSTEM_STUDENTS_DELETE))],
)
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db)):
    return await StudentService.delete_student(db, student_id)


@students_router.post(
    "/{student_id}/approve",
    response_model=StudentRead,
    dependencies=[Depends(require_permission("student.management.manage"))],
)
async def approve_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StudentService.approve_student(db, student_id, current_user)


@students_router.post(
    "/{student_id}/reject",
    response_model=StudentRead,
    dependencies=[Depends(require_permission("student.management.manage"))],
)
async def reject_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StudentService.reject_student(db, student_id, current_user)
