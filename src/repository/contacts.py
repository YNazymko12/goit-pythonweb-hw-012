"""Repository for managing contact-related database operations.

This module provides a repository pattern implementation for Contact entities,
handling all database operations including:
- CRUD operations for contacts
- Search functionality
- Birthday-related queries

All operations are user-scoped, ensuring data isolation between users.
"""

from typing import List

from sqlalchemy import select, or_, and_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import timedelta, date

from src.database.models import Contact, User
from src.schemas.contacts import ContactBase, ContactResponse


class ContactRepository:
    """Repository class for managing contacts in the database.

    This class provides methods for creating, reading, updating, and deleting
    contacts, as well as specialized queries like searching and finding upcoming
    birthdays. All operations are scoped to a specific user for data isolation.
    """
    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session for database operations.
        """
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """Retrieve a paginated list of contacts for a specific user.

        Args:
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.
            user (User): User whose contacts to retrieve.

        Returns:
            List[Contact]: List of contacts belonging to the user.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """Retrieve a specific contact by ID for a user.

        Args:
            contact_id (int): ID of the contact to retrieve.
            user (User): User who owns the contact.

        Returns:
            Contact | None: The contact if found and owned by the user, None otherwise.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """Create a new contact for a user.

        Args:
            body (ContactBase): Contact data from the request.
            user (User): User who will own the contact.

        Returns:
            Contact: The newly created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """Delete a contact owned by a user.

        Args:
            contact_id (int): ID of the contact to delete.
            user (User): User who owns the contact.

        Returns:
            Contact | None: The deleted contact if found and owned by the user, None otherwise.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """Update an existing contact owned by a user.

        Args:
            contact_id (int): ID of the contact to update.
            body (ContactBase): Updated contact data.
            user (User): User who owns the contact.

        Returns:
            Contact | None: The updated contact if found and owned by the user, None otherwise.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """Search for contacts matching a search term.

        Searches across multiple fields: first name, last name, email,
        additional data, and phone number. Case-insensitive search.

        Args:
            search (str): Search term to look for.
            skip (int): Number of records to skip for pagination.
            limit (int): Maximum number of records to return.
            user (User): User whose contacts to search.

        Returns:
            List[Contact]: List of contacts matching the search criteria.
        """
        stmt = (
            select(Contact)
            .filter(
                or_(
                    Contact.first_name.ilike(f"%{search}%"),
                    Contact.last_name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%"),
                    Contact.additional_data.ilike(f"%{search}%"),
                    Contact.phone_number.ilike(f"%{search}%"),
                ), Contact.user == user
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def upcoming_birthdays(self, user: User, days: int = 7,) -> List[Contact]:
        """Find contacts with birthdays in the upcoming days.

        Args:
            user (User): User whose contacts to check.
            days (int, optional): Number of days to look ahead. Defaults to 7.

        Returns:
            List[Contact]: List of contacts with birthdays in the specified period.
        """
        today = date.today()
        future_date = today + timedelta(days=days)

        stmt = select(Contact).filter(
            Contact.user == user,
        or_(
            and_(
                extract("month", Contact.birthday) == today.month,
                extract("day", Contact.birthday) >= today.day,
            ),
            and_(
                extract("month", Contact.birthday) == future_date.month,
                extract("day", Contact.birthday) <= future_date.day,
            ),
            and_(
                extract("month", Contact.birthday) > today.month,
                extract("month", Contact.birthday) < future_date.month,
            )
        )
    )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()