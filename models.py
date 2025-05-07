# Defines the database models for the application using SQLAlchemy.

from datetime import datetime, timezone # Import datetime for timestamping
from typing import Optional # For type hinting optional relationships
import sqlalchemy as sa # Core SQLAlchemy library
import sqlalchemy.orm as so # SQLAlchemy ORM components
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
from flask_login import UserMixin # Provides default implementations for Flask-Login user methods

# Import the db instance initialized in app/__init__.py
from app import db


class User(UserMixin, db.Model):
    """
    Represents a user in the application.
    Includes authentication fields and relationship to analysis results.
    Inherits from UserMixin for Flask-Login integration.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    # Add email column
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256)) # Store hashed password

    # Define the one-to-many relationship between User and Result
    # 'back_populates' links this relationship to the 'author' relationship in Result
    # 'lazy=select'' means results are loaded when accessed
    # 'cascade="all, delete-orphan"' ensures results are deleted if the user is deleted
    results: so.WriteOnlyMapped['Result'] = so.relationship(
        back_populates='author', lazy='select', cascade="all, delete-orphan"
    )

    def set_password(self, password: str):
        """
        Generates a salted hash for the given password and stores it.
        Args:
            password (str): The plain text password to hash.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Checks if the provided password matches the stored hash.
        Args:
            password (str): The plain text password to check.
        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        # Ensure password_hash is not None before checking
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """String representation of the User object."""
        return f'<User {self.username}>'

