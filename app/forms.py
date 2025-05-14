# Defines the WTForms used in the Flask application.
# Includes forms for user login, registration, and sentiment analysis submission.

from flask_wtf import FlaskForm # Base class for Flask-WTF forms
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, EmailField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email, Optional as WTFormsOptional, Regexp
import sqlalchemy as sa

# Import the User model to check for existing usernames during registration
try:
    # Updated to import new model names if necessary, User model is still User
    from .models import User, AnalysisReport, db 
except ImportError:
    User = None
    AnalysisReport = None # Add AnalysisReport here for context, though not directly used in all forms
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
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6),
        Regexp(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$',
            message="Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character."
        )
    ]) # Enforce minimum password length
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
            # raise ValidationError("Cannot validate username at this time. Please try again later.")

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
            # raise ValidationError("Cannot validate email at this time. Please try again later.")


class AnalysisForm(FlaskForm):
    """Form for submitting text for creating an analysis report."""
    report_name = StringField('Report Name (Optional)', validators=[WTFormsOptional(), Length(max=128)])
    news_text = TextAreaField('News Articles Text (one article per line or separated by double newlines)', 
                              validators=[DataRequired(), Length(min=10, max=50000)],
                              render_kw={"rows": 15, "placeholder": "Paste your news articles here. For multiple articles, place each on a new line or separate them with a blank line."})
    submit = SubmitField('Analyze and Create Report')


class ShareReportForm(FlaskForm):
    """Form for sharing an analysis report with another user."""
    # Renamed from ShareForm to ShareReportForm for clarity
    # This form might be part of a page where the report_id is implicit or passed in the URL
    share_with_username = StringField('Username to share with', validators=[DataRequired(), Length(max=64)])
    report_id = HiddenField() # To carry the report_id if needed, though often handled by URL context
    submit = SubmitField('Share Report')

    def validate_share_with_username(self, share_with_username):
        """
        Custom validator to check if the username to share with exists.
        Requires the User model and db session to be available.
        Args:
            share_with_username (Field): The username field being validated.
        Raises:
            ValidationError: If the username does not exist in the database.
        """
        if db and User:
            user = db.session.scalar(db.select(User).where(User.username == share_with_username.data))
            if user is None:
                raise ValidationError('User not found. Please enter a valid username.')
        else:
            print("Warning: DB connection or User model not available for username validation during sharing.")


class ManageSharingForm(FlaskForm):
    """Form for managing multiple sharing recipients."""
    users_to_share_with = SelectMultipleField('Select users to share with:',
                                             coerce=int,
                                             render_kw={"class": "form-select"})
    submit = SubmitField('Update Sharing Settings')