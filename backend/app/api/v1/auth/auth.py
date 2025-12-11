from app.api.v1.auth.schemas import (
    ActivateUserRequest,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetResponse,
    ValidateResetTokenRequest,
    ValidateResetTokenResponse,
)
from app.core.security import verify_password
from app.core.auth import AuthService, get_current_user
from app.core.utils import create_password_reset_token, verify_password_reset_token
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
from app.services.notification_service.workrs.worker import send_notification_task

auth_router = APIRouter(prefix="/auth")


# Public Register (Students)
@auth_router.post(
    "/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register_student(
    payload: RegisterRequest, db: AsyncSession = Depends(get_db)
):
    """
    Registration for students using NationalID as login_identifier.
    Email is optional, but phone is required.
    """
    try:
        # Check if NationalID already exists
        existing = await user_crud.get_by_login_identifier(db, payload.national_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NationalID already registered",
            )

        # Get default Student role
        result = await db.execute(select(Role).where(Role.name == "Student"))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default role 'student' not found",
            )

        # Create user
        user = User(
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            password_hash=get_password_hash(payload.password),
            role_id=role.id,
            login_identifier=payload.national_id,
            login_type="national_id",
            status=UserStatus.pending.value,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Create student profile
        student = Student(user_id=user.id, national_id=payload.national_id)
        db.add(student)
        await db.commit()
        await db.refresh(user, ["student"])

        return UserRead(
            id=user.id,
            full_name=user.full_name,
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


# Universal Login
@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_login_identifier(db, payload.identifier)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid identifier or password",
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid identifier or password",
        )

    if user.status != UserStatus.active.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not activated yet",
        )

    token = AuthService.generate_access_token_for_user(user)
    return TokenResponse(
        access_token=token,
        user=UserRead(
            id=user.id,
            full_name=user.full_name,
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
        full_name=current_user.full_name,
        email=current_user.email,
        role_name=current_user.role.name,
        status=current_user.status,
    )


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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Old password incorrect"
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
    user_id: int, payload: ChangePasswordRequest, db: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.password_hash = get_password_hash(payload.new_password)
    db.add(user)
    await db.commit()
    return {
        "message": f"Password for user {user.email or user.login_identifier} updated successfully"
    }


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


@auth_router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """
    Forgot password behavior:
    - If identifier is NationalID:
        → If user exists → allow direct reset (no email required)
    - If identifier is email:
        → Send reset link to user's email or parent's fallback
    """

    identifier = payload.identifier.strip()
    user = None
    is_email = False
    is_national = False

    # Determine identifier type
    if "@" in identifier:
        is_email = True
        user = await user_crud.get_by_email(db, identifier)

    elif identifier.isdigit() and len(identifier) == 14:
        is_national = True
        user = await user_crud.get_by_login_identifier(db, identifier)

    # Case 1: National ID → direct reset (if exists)
    if is_national and user:
        return {
            "direct_reset": True,
            "user_id": user.id,
            "message": "Proceed to reset password directly.",
        }

    # Case 2: Email → send reset link
    if is_email and user:
        token = create_password_reset_token(user.id)
        reset_link = f"http://localhost:5173/reset-password?token={token}"
        recipients: list[str] = []

        # Primary: user's email
        if user.email:
            recipients.append(user.email)

        # Fallback: parent's email(s)
        if not recipients and getattr(user, "student", None):
            for link in getattr(user.student, "parent_links", []):
                parent_email = getattr(link.parent.user, "email", None)
                if parent_email:
                    recipients.append(parent_email)

        # Send emails
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

    # If identifier is invalid or user not found → generic response
    return {
        "direct_reset": False,
        "message": "If the identifier is registered, password reset instructions have been sent.",
    }


@auth_router.post("/reset-password-direct", response_model=PasswordResetResponse)
async def reset_password_direct(
    payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    try:
        user_id = payload.user_id
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during direct password reset",
        )


@auth_router.get("/get-user-name/{user_id}")
async def get_user_name(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    return {"id": user.id, "full_name": user.full_name}


# Validate reset token
@auth_router.post("/validate-reset-token", response_model=ValidateResetTokenResponse)
async def validate_reset_token(payload: ValidateResetTokenRequest):
    try:
        user_id = verify_password_reset_token(payload.token)
        return ValidateResetTokenResponse(valid=True, user_id=user_id)
    except HTTPException:
        return ValidateResetTokenResponse(valid=False, user_id=None)


# Reset password using token
@auth_router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    try:
        user_id = verify_password_reset_token(payload.token)
    except HTTPException as e:
        raise e

    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
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
