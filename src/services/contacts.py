"""Contact management service layer.

This module provides a service layer for managing contacts, acting as an
intermediary between the API endpoints and the repository layer. It handles:
- Contact CRUD operations
- Contact search functionality
- Birthday-related queries

All operations are user-scoped to ensure proper data isolation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactBase, ContactResponse
from src.database.models import User, Contact


class ContactService:
    """Service class for managing contact operations.

    This class provides a higher-level interface for contact operations,
    delegating the actual database operations to the ContactRepository.
    It ensures all operations are properly scoped to the requesting user.
    """
    def __init__(self, db: AsyncSession):
        """Initialize the contact service.

        Args:
            db (AsyncSession): SQLAlchemy async session for database operations.
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """Create a new contact for a user.

        Args:
            body (ContactBase): Contact information to create.
            user (User): User who will own the contact.

        Returns:
            Contact: The newly created contact.
        """
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, user: User) -> list[Contact]:
        """Get a paginated list of contacts for a user.

        Args:
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.
            user (User): User whose contacts to retrieve.

        Returns:
            list[Contact]: List of contacts belonging to the user.
        """
        return await self.contact_repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User) -> Contact | None:
        """Get a specific contact by ID.

        Args:
            contact_id (int): ID of the contact to retrieve.
            user (User): User who owns the contact.

        Returns:
            Contact | None: The contact if found and owned by the user, None otherwise.
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactBase, user: User) -> Contact | None:
        """Update an existing contact.

        Args:
            contact_id (int): ID of the contact to update.
            body (ContactBase): Updated contact information.
            user (User): User who owns the contact.

        Returns:
            Contact | None: The updated contact if found and owned by the user, None otherwise.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """Delete a contact.

        Args:
            contact_id (int): ID of the contact to delete.
            user (User): User who owns the contact.

        Returns:
            Contact | None: The deleted contact if found and owned by the user, None otherwise.
        """
        return await self.contact_repository.remove_contact(contact_id, user)

    async def search_contacts(self, search: str, skip: int, limit: int, user: User) -> list[Contact]:
        """Search for contacts matching a search term.

        Args:
            search (str): Search term to look for.
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.
            user (User): User whose contacts to search.

        Returns:
            list[Contact]: List of contacts matching the search criteria.
        """
        return await self.contact_repository.search_contacts(search, skip, limit, user)

    async def upcoming_birthdays(self, days: int, user: User) -> list[Contact]:
        """Find contacts with birthdays in the upcoming days.

        Args:
            days (int): Number of days to look ahead.
            user (User): User whose contacts to check.

        Returns:
            list[Contact]: List of contacts with birthdays in the specified period.
        """
        return await self.contact_repository.upcoming_birthdays(days, user)