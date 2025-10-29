from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.api.v1.auth.jwt_handler import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
    return payload  # You can customize this to return a user model instead of just the payload
