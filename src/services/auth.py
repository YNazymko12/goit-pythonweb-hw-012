"""Authentication service module.

This module provides authentication-related functionality including:
- Password hashing and verification
- JWT token generation and validation
- User authentication middleware
- Email verification token handling

It uses bcrypt for password hashing and JWT for token generation.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.database.models import User


class Hash:
    """Password hashing utility class using bcrypt.

    This class provides methods for hashing passwords and verifying
    password hashes using the bcrypt algorithm.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password (str): The plain-text password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate a bcrypt hash of a password.

        Args:
            password (str): The plain-text password to hash.

        Returns:
            str: The bcrypt hash of the password.
        """
        return self.pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """Create a new JWT access token.

    Args:
        data (dict): The data to encode in the token, typically contains 'sub' key
            with the username.
        expires_delta (Optional[int], optional): Token expiration time in seconds.
            If None, uses the default from settings. Defaults to None.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency for getting the current authenticated user.

    Validates the JWT token and retrieves the corresponding user.
    First tries to get the user from Redis cache, if not found,
    retrieves from database and caches the result.

    Args:
        token (str): JWT token from the Authorization header.
        db (Session): Database session.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user is not found (401).
    """
    from src.services.redis_service import redis_service
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("scope") == "email_verification":
            raise credentials_exception
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Try to get user from cache first
    user = redis_service.get_user_from_cache(int(user_id))
    if user is not None:
        return user

    # If not in cache, get from database and cache it
    user_service = UserService(db)
    user = await user_service.get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    # Cache the user for future requests
    redis_service.cache_user(user)
    if user is None:
        raise credentials_exception
    return user

def create_email_token(data: dict) -> str:
    """Create a JWT token for email verification.

    Creates a token that expires in 7 days, used for email verification links.

    Args:
        data (dict): The data to encode in the token, typically contains 'sub' key
            with the email address.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

async def get_email_from_token(token: str) -> str:
    """Extract the email address from an email verification token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        str: The email address from the token.

    Raises:
        HTTPException: If the token is invalid or expired (422).
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )