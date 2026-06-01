from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from backend.api.schemas import UserToken as UserTokenSchema
from backend.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.logging_config import get_logger

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = get_logger(__name__)


@router.post("/token", response_model=UserTokenSchema)
def login(username: str, password: str):
    logger.info(f"Login attempt for user: {username}")
    if not username or not password:
        logger.warning("Login failed: missing credentials")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password required"
        )

    if password != "demo":
        logger.warning(f"Login failed for user {username}: invalid password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "scopes": ["read", "write"]},
        expires_delta=access_token_expires
    )
    logger.info(f"Login successful for user: {username}")
    return {"access_token": access_token, "token_type": "bearer"}
