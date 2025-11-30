from typing import List

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.core.utils import get_active_branch
from app.db.session import get_db
from app.modules.classes.crud import class_crud
from app.modules.classes.models import Class
from app.modules.classes.schemas import (
    ClassCreate,
    ClassRead,
    ClassStudentsResponse,
    ClassUpdate,
)
from app.modules.permissions.permissions import PermissionCode
from app.modules.students.models import Student, StudentClass
from app.modules.teachers.models import Teacher
from app.modules.users.models import User
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from fastapi_pagination import Page
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

classes_router = APIRouter(prefix="/classes", tags=["Classes"])


@classes_router.get(
    "/teacher-classes",
    response_model=List[ClassRead],
)
async def get_teachers_classes_with_header(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    active_branch_id: int = Depends(get_active_branch),
    _=[Depends(require_permission(PermissionCode.ACADEMIC_CLASSES_VIEW))],
):
    try:
        teacher_query = (
            select(Teacher)
            .where(Teacher.user_id == user.id)
            .options(selectinload(Teacher.classes))
        )
        result = await db.execute(teacher_query)
        teacher = result.scalar_one_or_none()

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher profile not found for this user",
            )

        branch_classes = [
            class_ for class_ in teacher.classes if class_.branch_id == active_branch_id
        ]

        return branch_classes

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching classes: {str(e)}",
        )


@classes_router.get(
    "/{class_id}/students/",
    response_model=List[ClassStudentsResponse],
    dependencies=[Depends(require_permission("academic.classes.view"))],
)
async def get_class_students_simple(
    class_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    _=[Depends(require_permission(PermissionCode.ACADEMIC_CLASSES_VIEW))],
):
    try:
        # Verify teacher access to this class
        teacher_class_check = select(Class).where(
            Class.id == class_id, Class.teachers.any(user_id=user.id)
        )
        result = await db.execute(teacher_class_check)
        class_obj = result.scalar_one_or_none()

        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this class",
            )

        query = (
            select(Student.id.label("student_id"), User.full_name)
            .select_from(StudentClass)
            .join(Student, Student.id == StudentClass.student_id)
            .join(User, User.id == Student.user_id)
            .where(StudentClass.class_id == class_id)
        )

        result = await db.execute(query)
        students = result.all()

        return [
            ClassStudentsResponse(student_id=row.student_id, full_name=row.full_name)
            for row in students
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching class students: {str(e)}",
        )


@classes_router.get(
    "/",
    response_model=Page[ClassRead],
)
async def list_classes(
    request: Request,
    branch_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    classes = await class_crud.get_all(db, request=request)
    return classes


# @classes_router.get("/by-branch/{branch_id}", response_model=List[ClassRead])
# async def get_classes_by_branch(
#     branch_id: int,
#     request: Request,
#     db: AsyncSession = Depends(get_db),
# ):
#     classes = await class_crud.get_by_id(db, branch_id=branch_id)
#     if not classes:
#         raise HTTPException(status_code=404, detail="No classes found for this branch")
#     return [ClassRead.from_orm(c) for c in classes]


@classes_router.post("/by-branchs", response_model=List[ClassRead])
async def get_classes_by_branchs(
    branch_ids: List[int] = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    classes = await class_crud.get_class_by_branch(db, branch_ids=branch_ids)
    if not classes:
        raise HTTPException(status_code=404, detail="No classes found for this branch")
    return [ClassRead.from_orm(c) for c in classes]


@classes_router.get("/{class_id}", response_model=ClassRead)
async def get_class(class_id: int, db: AsyncSession = Depends(get_db)):
    class_ = await class_crud.get_by_id(db, class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_


@classes_router.post(
    "/",
    response_model=ClassRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("academic.classes.add")),
    ],
)
async def create_class(class_in: ClassCreate, db: AsyncSession = Depends(get_db)):
    return await class_crud.create(db, class_in)


@classes_router.put(
    "/{class_id}",
    response_model=ClassRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("academic.classes.edit")),
    ],
)
async def update_class(
    class_id: int, class_in: ClassUpdate, db: AsyncSession = Depends(get_db)
):
    class_ = await class_crud.get_by_id(db, class_id, request=None)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return await class_crud.update(db, class_, class_in)


@classes_router.delete(
    "/{class_id}",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("academic.classes.delete")),
    ],
)
async def delete_class(class_id: int, db: AsyncSession = Depends(get_db)):
    await class_crud.delete(db, class_id)
    return None
