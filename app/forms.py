# Defines the WTForms used in the Flask application.
# Includes forms for user login, registration, and sentiment analysis submission.

from flask_wtf import FlaskForm # Base class for Flask-WTF forms
# Import EmailField and Email validator
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, EmailField
# Import Email validator
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email

# Import the User model to check for existing usernames during registration
# It's assumed 'User' is defined in models.py within the same 'app' package
# You might need to adjust the import based on your final db initialization strategy
try:
    from .models import User, db # Keep this import
except ImportError:
    User = None
    db = None # Explicitly set db to None if import fails


class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me') # Option to keep the user logged in
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Form for new user registration."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    # Add EmailField for email input
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)]) # Enforce minimum password length
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]) # Ensure passwords match
    submit = SubmitField('Register')

    def validate_username(self, username):
        """
        Custom validator to check if the username is already taken.
        Requires the User model and db session to be available.
        Args:
            username (Field): The username field being validated.
        Raises:
            ValidationError: If the username already exists in the database.
        """
        # Check if db and User were imported successfully
        if db and User:
            # Use Flask-SQLAlchemy's db.session and db.select
            user = db.session.scalar(db.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')
        else:
            # Log or handle the case where db/User isn't available
            # Depending on strictness, you might raise an error or just log a warning
            print("Warning: DB connection or User model not available for username validation.")
            # Optionally, raise an exception if validation cannot proceed:
            raise ValidationError("Cannot validate username at this time. Please try again later.")

    # Add validation for email uniqueness
    def validate_email(self, email):
        """
        Custom validator to check if the email is already registered.
        Requires the User model and db session to be available.
        Args:
            email (Field): The email field being validated.
        Raises:
            ValidationError: If the email already exists in the database.
        """
        if db and User:
            user = db.session.scalar(db.select(User).where(User.email == email.data))
            if user is not None:
                raise ValidationError('Please use a different email address.')
        else:
            print("Warning: DB connection or User model not available for email validation.")
            # Optionally, raise an exception if validation cannot proceed:
            raise ValidationError("Cannot validate email at this time. Please try again later.")


class AnalysisForm(FlaskForm):
    """Form for submitting text for sentiment analysis."""
    news_text = TextAreaField(
        'News Text',
        validators=[DataRequired(), Length(min=10, max=10000)], # Require text, set length limits
        render_kw={"placeholder": "Paste news text here..."} # Add placeholder text to the textarea
    )
    submit = SubmitField('Analyze Sentiment')