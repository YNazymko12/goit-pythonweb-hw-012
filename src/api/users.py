"""User management API endpoints.

This module provides FastAPI routes for managing user-related operations, including:
- Getting current user information
- Updating user avatar

All endpoints require user authentication and some have rate limiting applied.
"""

from fastapi import APIRouter, Depends, Request, File, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession  
from src.schemas.users import User
from src.services.auth import get_current_user
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.conf.config import settings
from src.database.db import get_db


limiter = Limiter(key_func=get_remote_address)


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User, description="No more than 5 requests per minute")
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)) -> User:
    """Get information about the currently authenticated user.

    This endpoint is rate-limited to 5 requests per minute.

    Args:
        request (Request): FastAPI request object for rate limiting.
        user (User): Currently authenticated user from token.

    Returns:
        User: Current user's information.
    """
    return user

@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update the user's avatar by uploading a new image.

    The image will be uploaded to Cloudinary and the URL will be stored in the user's profile.

    Args:
        file (UploadFile): The image file to upload.
        user (User): Currently authenticated user.
        db (AsyncSession): Database session dependency.

    Returns:
        User: Updated user information with new avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user