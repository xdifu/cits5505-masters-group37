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
    """
    Form for submitting text content for sentiment analysis.
    
    Fields:
        report_name: Optional name for the analysis report
        news_text: Text area for multiple news articles input
        keywords: Optional keywords for focused analysis
        submit: Submit button for form
    """
    report_name = StringField(
        'Report Name (Optional)', 
        validators=[
            WTFormsOptional(),
            Length(max=128),
            Regexp(r'^[\w\s-]*$', message="Report name can only contain letters, numbers, spaces and hyphens")
        ]
    )
    
    news_text = TextAreaField(
        'News Articles Text', 
        validators=[
            DataRequired(message="Please enter at least one news article"),
            Length(min=10, max=50000, message="Text must be between 10 and 50000 characters")
        ],
        render_kw={
            "rows": 15,
            "class": "form-control",
            "placeholder": "Paste your news articles here. Separate multiple articles with blank lines."
        }
    )
    
    # New field for analysis keywords
    keywords = StringField(
        'Focus Keywords (Optional)',
        validators=[
            WTFormsOptional(),
            Length(max=200),
            Regexp(r'^[\w\s,]*$', message="Keywords should be comma-separated words")
        ],
        render_kw={
            "placeholder": "Enter comma-separated keywords (optional)"
        }
    )
    
    submit = SubmitField('Analyze Content')

    def validate_news_text(self, field):
        """
        Custom validator for news_text field.
        Ensures the text contains valid content and proper formatting.
        
        Args:
            field: The news_text field being validated
            
        Raises:
            ValidationError: If text format is invalid
        """
        articles = [art.strip() for art in field.data.split('\n\n') if art.strip()]
        if not articles:
            raise ValidationError('Please provide at least one valid article')
        if len(articles) > 50:
            raise ValidationError('Maximum 50 articles allowed per analysis')


class ShareReportForm(FlaskForm):
    """
    Form for sharing analysis reports with other users.
    Handles both single user sharing and batch sharing operations.
    
    Fields:
        share_with_username: Username of recipient
        report_id: Hidden field for report identification
        share_message: Optional message for recipient
        submit: Submit button
    """
    share_with_username = StringField(
        'Share with User',
        validators=[
            DataRequired(),
            Length(min=3, max=64),
            Regexp(r'^[\w.-]+$', message="Username contains invalid characters")
        ]
    )
    
    report_id = HiddenField(validators=[DataRequired()])
    
    # New field for share message
    share_message = TextAreaField(
        'Add a Message (Optional)',
        validators=[
            WTFormsOptional(),
            Length(max=500)
        ],
        render_kw={
            "rows": 3,
            "placeholder": "Add an optional message for the recipient"
        }
    )
    
    submit = SubmitField('Share Report')

    def validate_share_with_username(self, share_with_username):
        """
        Validates share recipient exists and has permission to receive shares.
        
        Args:
            share_with_username: Username field to validate
            
        Raises:
            ValidationError: If user not found or sharing not allowed
        """
        if not (db and User):
            raise ValidationError("System error: Unable to validate user")
            
        user = db.session.scalar(
            db.select(User).where(User.username == share_with_username.data)
        )
        
        if user is None:
            raise ValidationError('User not found')
        
        if user.id == current_user.id:
            raise ValidationError('Cannot share with yourself')
            
        # Check if already shared
        if self.report_id.data:
            existing_share = db.session.scalar(
                db.select(analysis_report_shares).where(
                    analysis_report_shares.c.analysis_report_id == self.report_id.data,
                    analysis_report_shares.c.recipient_id == user.id
                )
            )
            if existing_share:
                raise ValidationError('Report already shared with this user')