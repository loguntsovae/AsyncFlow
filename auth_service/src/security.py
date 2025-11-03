from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import logging
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from passlib.context import CryptContext

from settings import settings
from db.base import get_db
from db.models.users import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ---
# Парольный контекст:
#  - основная схема: bcrypt_sha256 (снимает лимит 72 байта)
#  - legacy: bcrypt (чтобы проверять уже сохранённые хэши)
# ---
pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    default="bcrypt_sha256",
    deprecated="auto",
)

# Корректный относительный URL для токена (через ваш /auth/token endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ---
# Хэширование и верификация
# ---

def get_password_hash(password: str) -> str:
    """
    Возвращает хэш пароля, используя bcrypt_sha256 (по умолчанию).
    ВНИМАНИЕ: пароль не логируем.
    """
    if not isinstance(password, str):
        raise TypeError("password must be a str")
    # passlib сам все корректно кодирует; лимиты 72 байта для 'bcrypt' нас не касаются,
    # т.к. основная схема 'bcrypt_sha256' предварительно хэширует пароль SHA-256.
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет пароль против хэша (поддерживает и bcrypt_sha256, и legacy bcrypt).
    """
    if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as exc:
        logger.warning("Password verification failed: %s", exc.__class__.__name__)
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)  # Use AsyncSession
) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        sa.select(User).where(User.username == username)
    )
    user = result.scalar()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user