"""SQLAlchemy models for the application.

This module defines the database models using SQLAlchemy ORM, including:
- Base class with common timestamp fields
- Contact model for storing contact information
- User model for user authentication and profile data

All models inherit from Base which provides created_at and updated_at timestamps.
"""

from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Boolean, func, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DateTime, Date


class Base(DeclarativeBase):
    """Base class for all models.

    Provides common timestamp fields for tracking creation and modification times.

    Attributes:
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
    """
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class Contact(Base):
    """Contact model for storing contact information.

    Represents a contact in the address book. Each contact belongs to a user
    and contains personal information like name, email, phone number, and birthday.

    Attributes:
        id (int): Primary key.
        first_name (str): Contact's first name, max 50 characters.
        last_name (str): Contact's last name, max 50 characters.
        email (str): Contact's email address, max 100 characters.
        phone_number (str): Contact's phone number, max 20 characters.
        birthday (date): Contact's birthday.
        additional_data (str): Optional additional information, max 150 characters.
        user_id (int): Foreign key to the users table.
        user (User): Relationship to the User model.
    """
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    additional_data: Mapped[str] = mapped_column(String(150), nullable=True)

    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None)
    user = relationship("User", backref="contacts")

class User(Base):
    """User model for authentication and profile information.

    Represents a user in the system. Stores authentication information,
    profile details, and has a relationship to contacts. Each user can
    have multiple contacts.

    Attributes:
        id (int): Primary key.
        username (str): Unique username for the user.
        email (str): Unique email address.
        hashed_password (str): Bcrypt hashed password.
        created_at (datetime): Account creation timestamp.
        avatar (str): URL to user's avatar image, max 255 characters.
        confirmed (bool): Email confirmation status, defaults to False.
        contacts (List[Contact]): List of contacts belonging to this user (backref).
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)