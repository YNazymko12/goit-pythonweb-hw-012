"""User management service layer.

This module provides a service layer for managing users, acting as an
intermediary between the API endpoints and the repository layer. It handles:
- User registration with Gravatar integration
- User lookup by various identifiers
- Email confirmation
- Avatar management

The service integrates with Gravatar for automatic avatar generation
during user registration.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas.users import UserCreate
from src.database.models import User


class UserService:
    """Service class for managing user operations.

    This class provides a higher-level interface for user operations,
    delegating the actual database operations to the UserRepository.
    It integrates with external services like Gravatar for enhanced
    user profile functionality.
    """
    def __init__(self, db: AsyncSession):
        """Initialize the user service.

        Args:
            db (AsyncSession): SQLAlchemy async session for database operations.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate) -> User:
        """Create a new user with an optional Gravatar avatar.

        Attempts to fetch a Gravatar image for the user's email. If the Gravatar
        service is unavailable or encounters an error, the user will be created
        without an avatar.

        Args:
            body (UserCreate): User registration information including email
                and password.

        Returns:
            User: The newly created user entity.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by their ID.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            User | None: The user if found, None otherwise.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieve a user by their username.

        Args:
            username (str): The username to look up.

        Returns:
            User | None: The user if found, None otherwise.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email (str): The email address to look up.

        Returns:
            User | None: The user if found, None otherwise.
        """
        return await self.repository.get_user_by_email(email)
    
    async def confirmed_email(self, email: str) -> bool:
        """Mark a user's email as confirmed.

        Args:
            email (str): The email address to confirm.

        Returns:
            bool: True if the email was confirmed successfully, False otherwise.
        """
        return await self.repository.confirmed_email(email)
    
    async def update_avatar_url(self, email: str, avatar_url: str) -> User | None:
        """Update a user's avatar URL.

        Args:
            email (str): The email address of the user.
            avatar_url (str): The new avatar URL to set.

        Returns:
            User | None: The updated user if found, None otherwise.
        """
        return await self.repository.update_avatar_url(email, avatar_url)

