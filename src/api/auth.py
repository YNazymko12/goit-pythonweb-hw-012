"""Authentication API endpoints for user registration, login, and email confirmation.

This module provides FastAPI routes for handling user authentication operations including:
- User registration with email confirmation
- User login with JWT token generation
- Email confirmation request and verification
"""

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.users import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, get_email_from_token, Hash
from src.services.users import UserService
from src.services.email import send_email
from src.database.db import get_db
from src.conf.messages import API_ERROR_USER_ALREADY_EXIST, API_ERROR_USER_NOT_AUTHORIZED, API_ERROR_LOGIN_OR_PASSWORD

router = APIRouter(prefix="/auth", tags=["auth"])

# Реєстрація користувача
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Register a new user and send confirmation email.

    Args:
        user_data (UserCreate): User registration data including email, username, and password.
        background_tasks (BackgroundTasks): FastAPI background tasks handler for sending emails.
        request (Request): FastAPI request object for getting base URL.
        db (Session): Database session dependency.

    Returns:
        User: Created user object.

    Raises:
        HTTPException: If user with provided email or username already exists (409).
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=API_ERROR_USER_ALREADY_EXIST,
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user

# Логін користувача
@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """Authenticate user and generate access token.

    Args:
        form_data (OAuth2PasswordRequestForm): Form containing username and password.
        db (Session): Database session dependency.

    Returns:
        Token: JWT access token for authenticated user.

    Raises:
        HTTPException: If login credentials are invalid (401) or email is not confirmed (401).
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=API_ERROR_LOGIN_OR_PASSWORD,
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=API_ERROR_USER_NOT_AUTHORIZED,
        )
    # Store user ID in token and cache the user
    from src.services.redis_service import redis_service
    access_token = await create_access_token(data={"sub": str(user.id)})
    redis_service.cache_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Request email confirmation to be sent again.

    Args:
        body (RequestEmail): Request body containing email address.
        background_tasks (BackgroundTasks): FastAPI background tasks handler for sending emails.
        request (Request): FastAPI request object for getting base URL.
        db (Session): Database session dependency.

    Returns:
        dict: Message indicating the status of the request.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict:
    """Confirm user's email address using the provided token.

    Args:
        token (str): Email confirmation token.
        db (Session): Database session dependency.

    Returns:
        dict: Message indicating the confirmation status.

    Raises:
        HTTPException: If verification fails (400) or token is invalid.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}