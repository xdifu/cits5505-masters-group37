# Defines the database models for the application using SQLAlchemy.
# Includes models for Users and their sentiment analysis Results.

from datetime import datetime, timezone # Import datetime for timestamping
from typing import Optional, List # For type hinting optional relationships and lists
import sqlalchemy as sa # Core SQLAlchemy library
import sqlalchemy.orm as so # SQLAlchemy ORM components
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
from flask_login import UserMixin # Provides default implementations for Flask-Login user methods

# Import the db instance initialized in app/__init__.py
from app import db, login_manager

# Association table for Result sharing
result_shares = db.Table('result_shares',
    db.Column('result_id', sa.Integer, db.ForeignKey('result.id'), primary_key=True),
    db.Column('recipient_id', sa.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """
    Represents a user in the application.
    Includes authentication fields and relationship to analysis results.
    Inherits from UserMixin for Flask-Login integration.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True, nullable=False)
    # Add email column
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True, nullable=False)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=False) # Store hashed password

    # Define the one-to-many relationship between User and Result (results authored by the user)
    # 'back_populates' links this relationship to the 'author' relationship in Result
    # 'lazy=select'' means results are loaded when accessed
    # 'cascade="all, delete-orphan"' ensures results are deleted if the user is deleted
    # 'passive_deletes=True' allows cascading deletions without loading all related items
    authored_results: so.WriteOnlyMapped['Result'] = so.relationship(
        back_populates='author', lazy='select', 
        cascade="all, delete-orphan", passive_deletes=True
    )

    # Results shared with this user by others
    # Using string reference 'Result' to avoid forward reference issues
    results_shared_with_me: so.WriteOnlyMapped['Result'] = so.relationship(
        secondary=result_shares,
        primaryjoin=(result_shares.c.recipient_id == id),
        secondaryjoin="result_shares.c.result_id == Result.id", # Using string reference
        back_populates='shared_with_recipients',
        lazy='dynamic',
        passive_deletes=True
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
    Includes the original text, the sentiment, timestamp.
    Linked to a User via a foreign key (author).
    Can be shared with multiple other Users via a many-to-many relationship.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    original_text: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False) # Store the full text submitted
    sentiment: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False) # 'Positive', 'Neutral', 'Negative'
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc) # Default to current UTC time
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True, nullable=False) # Foreign key linking to User
    # Legacy field - kept for backward compatibility with existing schema
    shared: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, index=True)

    # Define the many-to-one relationship from Result to User (author)
    # 'back_populates' links this relationship to the 'results' relationship in User
    author: so.Mapped[User] = so.relationship(back_populates='authored_results')

    # Users this result is shared with
    # Using string reference 'User' to avoid forward reference issues
    shared_with_recipients: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=result_shares,
        primaryjoin=(result_shares.c.result_id == id),
        secondaryjoin="result_shares.c.recipient_id == User.id", # Using string reference
        back_populates='results_shared_with_me',
        lazy='dynamic',
        passive_deletes=True
    )

    def __repr__(self):
        """String representation of the Result object."""
        return f'<Result {self.id} - Sentiment: {self.sentiment}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))