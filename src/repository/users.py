"""Repository for managing user-related database operations.

This module provides a repository pattern implementation for User entities,
handling all database operations including:
- User creation and retrieval
- Email confirmation
- Avatar management
- User lookup by various identifiers
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserCreate


class UserRepository:
    """Repository class for managing users in the database.

    This class provides methods for creating and retrieving users,
    managing email confirmation status, and updating user avatars.
    It ensures proper data access patterns and encapsulates all
    user-related database operations.
    """
    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session for database operations.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by their ID.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            User | None: The user if found, None otherwise.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Retrieve a user by their username.

        Args:
            username (str): The username to look up.

        Returns:
            User | None: The user if found, None otherwise.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email (str): The email address to look up.

        Returns:
            User | None: The user if found, None otherwise.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """Create a new user in the database.

        Args:
            body (UserCreate): User creation data including username, email, and password.
            avatar (str, optional): URL to user's avatar image. Defaults to None.

        Returns:
            User: The newly created user object.

        Note:
            The password from the body is expected to be already hashed.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def confirmed_email(self, email: str) -> None:
        """Mark a user's email as confirmed.

        Args:
            email (str): Email address of the user to confirm.

        Note:
            This method assumes the user exists. The caller should verify
            the user exists before calling this method.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()
    
    async def update_avatar_url(self, email: str, url: str) -> User:
        """Update a user's avatar URL.

        Args:
            email (str): Email address of the user to update.
            url (str): New avatar URL.

        Returns:
            User: The updated user object.

        Note:
            This method assumes the user exists. The caller should verify
            the user exists before calling this method.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

