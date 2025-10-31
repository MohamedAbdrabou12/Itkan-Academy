from app.api.v1.auth.schemas import (
    ActivateUserRequest,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)
from app.core.auth import AuthService, get_current_user
from app.core.authorization import require_permission
from app.core.security import get_password_hash
from app.db.session import get_db
from app.modules.roles.models import Role
from app.modules.students.models import Student
from app.modules.users.crud import user_crud
from app.modules.users.models import User, UserStatus
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter(prefix="/auth")


# Public Register (Students)
@auth_router.post(
    "/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register_student(
    payload: RegisterRequest, db: AsyncSession = Depends(get_db)
):
    """
    Public endpoint for student registration.
    """
    try:
        # Check if email already exists
        existing = await user_crud.get_by_email(db, payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Get Student role
        result = await db.execute(select(Role).where(Role.name == "Student"))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default role 'student' not found",
            )

        # Create User
        user = User(
            name=payload.name,
            email=payload.email,
            password_hash=get_password_hash(payload.password),
            role_id=role.id,
            phone=payload.phone,
            status=UserStatus.pending,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        student = Student(
            parent_name=payload.parent_name,
            user_id=user.id,
            branch_id=payload.branch_id,
        )

        db.add(student)
        await db.commit()
        await db.refresh(user)

        return UserRead(
            id=user.id,
            name=user.name,
            email=user.email,
            role_name=role.name,
            status=user.status,
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration",
        )


# Login
@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if user.status != UserStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is not activated yet"
        )

    token = AuthService.generate_access_token_for_user(user)

    return TokenResponse(
        access_token=token,
        user=UserRead(
            id=user.id,
            name=user.name,
            email=user.email,
            role_name=user.role.name,
            status=user.status,
        ),
    )


# Get current authenticated user
@auth_router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserRead(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role_name=current_user.role.name,
        status=current_user.status,
    )


# Change password for self
@auth_router.put("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    valid_user = await AuthService.authenticate_user(
        db, current_user.email, payload.old_password
    )
    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Old password incorrect"
        )

    current_user.password_hash = get_password_hash(payload.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password updated successfully"}


# Change password for another user (admin-level)
@auth_router.put(
    "/change-password/{user_id}",
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:update")),
    ],
)
async def admin_change_password(
    user_id: int,
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.password_hash = get_password_hash(payload.new_password)
    db.add(user)
    await db.commit()
    return {"message": f"Password for user {user.email} updated successfully"}


# Update user status (admin approval)
@auth_router.put(
    "/update-status",
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:approve")),
    ],
)
async def update_user_status(
    payload: ActivateUserRequest, db: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_by_id(db, payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.status = payload.new_status
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": f"User status updated to {user.status}"}
