# Defines the database models for the application using SQLAlchemy.
# Includes models for Users and their sentiment analysis Results.

from datetime import datetime, timezone # Import datetime for timestamping
from typing import Optional # For type hinting optional relationships
import sqlalchemy as sa # Core SQLAlchemy library
import sqlalchemy.orm as so # SQLAlchemy ORM components
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
from flask_login import UserMixin # Provides default implementations for Flask-Login user methods

# It's assumed that 'db' is the SQLAlchemy instance initialized in app/__init__.py
# from app import db # Typically you would import db from your app factory or __init__

# Temporary placeholder for db until it's properly initialized in __init__.py
# In a real setup, remove this and use the imported 'db' from your app instance.
# You will need to replace this with the actual db instance from your app factory.
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    Represents a user in the application.
    Includes authentication fields and relationship to analysis results.
    Inherits from UserMixin for Flask-Login integration.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
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


class Result(db.Model):
    """
    Represents a single sentiment analysis result stored in the database.
    Includes the original text, the sentiment, timestamp, and sharing status.
    Linked to a User via a foreign key.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    original_text: so.Mapped[str] = so.mapped_column(sa.Text) # Store the full text submitted
    sentiment: so.Mapped[str] = so.mapped_column(sa.String(10)) # 'Positive', 'Neutral', 'Negative'
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc) # Default to current UTC time
    )
    shared: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, index=True) # Flag for sharing status
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True) # Foreign key linking to User

    # Define the many-to-one relationship from Result to User
    # 'back_populates' links this relationship to the 'results' relationship in User
    author: so.Mapped[User] = so.relationship(back_populates='results')

    def __repr__(self):
        """String representation of the Result object."""
        return f'<Result {self.id} Sentiment: {self.sentiment}>'