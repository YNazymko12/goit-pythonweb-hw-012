"""Contact management API endpoints.

This module provides FastAPI routes for managing contacts, including:
- Creating, reading, updating, and deleting contacts
- Searching contacts by text
- Getting upcoming birthdays
- Listing all contacts with pagination

All endpoints require user authentication.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.contacts import ContactBase, ContactResponse, ContactBirthdayRequest
from src.services.contacts import ContactService

from src.database.models import User
from src.services.auth import get_current_user

from src.conf import messages

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK)
async def read_contacts(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
) -> List[ContactResponse]:
    """Get a paginated list of contacts for the authenticated user.

    Args:
        skip (int, optional): Number of contacts to skip. Defaults to 0.
        limit (int, optional): Maximum number of contacts to return. Defaults to 100.
        db (AsyncSession): Database session dependency.
        user (User): Currently authenticated user.

    Returns:
        List[ContactResponse]: List of contacts belonging to the user.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),) -> ContactResponse:
    """Get a specific contact by ID.

    Args:
        contact_id (int): ID of the contact to retrieve.
        db (AsyncSession): Database session dependency.
        user (User): Currently authenticated user.

    Returns:
        ContactResponse: Contact details.

    Raises:
        HTTPException: If contact is not found (404).
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactBase, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),) -> ContactResponse:
    """Create a new contact.

    Args:
        body (ContactBase): Contact information to create.
        db (AsyncSession): Database session dependency.
        user (User): Currently authenticated user.

    Returns:
        ContactResponse: Created contact details.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactBase, contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),
) -> ContactResponse:
    """Update an existing contact.

    Args:
        body (ContactBase): Updated contact information.
        contact_id (int): ID of the contact to update.
        db (AsyncSession): Database session dependency.
        user (User): Currently authenticated user.

    Returns:
        ContactResponse: Updated contact details.

    Raises:
        HTTPException: If contact is not found (404).
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),) -> None:
    """Delete a contact.

    Args:
        contact_id (int): ID of the contact to delete.
        db (AsyncSession): Database session dependency.
        user (User): Currently authenticated user.

    Raises:
        HTTPException: If contact is not found (404).

    Returns:
        None
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    text: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),
) -> List[ContactResponse]:
    """Search contacts by text.

    Args:
        text (str): Search query text.
        skip (int, optional): Number of contacts to skip. Defaults to 0.
        limit (int, optional): Maximum number of contacts to return. Defaults to 100.
        db (AsyncSession): Database session dependency.
        user (User): Currently authenticated user.

    Returns:
        List[ContactResponse]: List of contacts matching the search criteria.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(text, skip, limit, user)
    return contacts


@router.post("/upcoming-birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(
    body: ContactBirthdayRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),
) -> List[ContactResponse]:
    """Get contacts with upcoming birthdays.

    Args:
        body (ContactBirthdayRequest): Request containing number of days to look ahead.
        db (AsyncSession): Database session dependency.
        user (User): Currently authenticated user.

    Returns:
        List[ContactResponse]: List of contacts with birthdays in the specified period.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.upcoming_birthdays(body.days, user)
    return contacts