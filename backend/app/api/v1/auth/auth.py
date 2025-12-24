from app.api.v1.auth.schemas import (
    ActivateUserRequest,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserRead,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetResponse,
    ValidateResetTokenRequest,
    ValidateResetTokenResponse,
)
from app.core.security import verify_password, get_password_hash
from app.core.auth import AuthService, get_current_user
from app.core.utils import create_password_reset_token, verify_password_reset_token
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.roles.models import Role
from app.modules.students.models import Student
from app.modules.users.crud import user_crud
from app.modules.users.models import User, UserStatus
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.notification_service.workrs.worker import send_notification_task

auth_router = APIRouter(prefix="/auth")


# Public Register (Students)
@auth_router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_student(
    payload: RegisterRequest, db: AsyncSession = Depends(get_db)
):
    existing = await user_crud.get_by_login_identifier(db, payload.national_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NationalID already registered",
        )

    if payload.email:
        existing_email = await user_crud.get_by_email(db, payload.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    result = await db.execute(select(Role).where(Role.name == "Student"))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default role 'Student' not found",
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        role_id=role.id,
        login_identifier=payload.national_id,
        login_type="national_id",
        status=UserStatus.pending,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    student = Student(user_id=user.id, national_id=payload.national_id)
    db.add(student)
    await db.commit()

    return user


# Universal Login
@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_login_identifier(db, payload.identifier)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid identifier or password",
        )

    if user.status != UserStatus.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not activated yet",
        )

    token = AuthService.generate_access_token_for_user(user)
    return {"access_token": token, "user": user}


# Get current user
@auth_router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# Password management
@auth_router.put("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    valid_user = await AuthService.authenticate_user(
        db, current_user.login_identifier, payload.old_password
    )
    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password incorrect",
        )

    current_user.password_hash = get_password_hash(payload.new_password)
    db.add(current_user)
    await db.commit()
    return {"message": "Password updated successfully"}


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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password_hash = get_password_hash(payload.new_password)
    db.add(user)
    await db.commit()
    return {
        "message": f"Password for user {user.email or user.login_identifier} updated successfully"
    }


# Update user status
@auth_router.put(
    "/update-status",
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:approve")),
    ],
)
async def update_user_status(
    payload: ActivateUserRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_by_id(db, payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.status = payload.new_status
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"message": f"User status updated to {user.status}"}


# Forgot password
@auth_router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    identifier = payload.identifier.strip()
    user = None

    if "@" in identifier:
        user = await user_crud.get_by_email(db, identifier)

    elif identifier.isdigit() and len(identifier) == 14:
        user = await user_crud.get_by_login_identifier(db, identifier)

    if identifier.isdigit() and len(identifier) == 14 and user:
        return {
            "direct_reset": True,
            "user_id": user.id,
            "message": "Proceed to reset password directly.",
        }

    if "@" in identifier and user:
        token = create_password_reset_token(user.id)
        reset_link = f"http://localhost:5173/reset-password?token={token}"

        recipients: list[str] = []
        if user.email:
            recipients.append(user.email)

        if not recipients and getattr(user, "student", None):
            for link in getattr(user.student, "parent_links", []):
                parent_email = getattr(link.parent.user, "email", None)
                if parent_email:
                    recipients.append(parent_email)

        for email in recipients:
            try:
                send_notification_task.delay(
                    user_id=user.id,
                    channel="email",
                    template_type="reset_password",
                    payload={
                        "username": user.full_name,
                        "reset_link": reset_link,
                        "email": email,
                    },
                )
            except Exception:
                pass

        return {
            "direct_reset": False,
            "message": "If this email is registered, a reset link has been sent.",
        }

    return {
        "direct_reset": False,
        "message": "If the identifier is registered, password reset instructions have been sent.",
    }


# Reset password (direct)
@auth_router.post("/reset-password-direct", response_model=PasswordResetResponse)
async def reset_password_direct(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_by_id(db, payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password_hash = get_password_hash(payload.new_password)
    if user.status != UserStatus.active:
        user.status = UserStatus.active

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return PasswordResetResponse(
        message="Password has been updated. You can now log in."
    )


# Get user name
@auth_router.get("/get-user-name/{user_id}")
async def get_user_name(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    return {"id": user.id, "full_name": user.full_name}


# Validate reset token
@auth_router.post(
    "/validate-reset-token",
    response_model=ValidateResetTokenResponse,
)
async def validate_reset_token(payload: ValidateResetTokenRequest):
    try:
        user_id = verify_password_reset_token(payload.token)
        return ValidateResetTokenResponse(valid=True, user_id=user_id)
    except HTTPException:
        return ValidateResetTokenResponse(valid=False, user_id=None)


# Reset password (token)
@auth_router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    user_id = verify_password_reset_token(payload.token)

    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password_hash = get_password_hash(payload.new_password)
    if user.status != UserStatus.active:
        user.status = UserStatus.active

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return PasswordResetResponse(
        message="Password has been updated. You can now log in."
    )
