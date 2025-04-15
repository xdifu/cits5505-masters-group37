# Defines the WTForms used in the Flask application.
# Includes forms for user login, registration, and sentiment analysis submission.

from flask_wtf import FlaskForm # Base class for Flask-WTF forms
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField # Import field types
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError # Import validators

# Import the User model to check for existing usernames during registration
# It's assumed 'User' is defined in models.py within the same 'app' package
# You might need to adjust the import based on your final db initialization strategy
try:
    from .models import User, db
except ImportError:
    # This is a fallback for environments where models might not be fully initialized yet
    # or if db is not directly available for import.
    # The validation logic relies on querying the User model.
    User = None


class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me') # Option to keep the user logged in
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Form for new user registration."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
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
        if User: # Check if the User model was imported successfully
            # It's assumed 'db.session' is available here.
            # This might require passing the db instance or using current_app context.
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')
        else:
            # Handle case where User model isn't available (e.g., during initial setup)
            # This validation might be skipped or handled differently depending on app structure.
            print("Warning: User model not available for username validation.")


class AnalysisForm(FlaskForm):
    """Form for submitting text for sentiment analysis."""
    news_text = TextAreaField(
        'News Text',
        validators=[DataRequired(), Length(min=10, max=10000)], # Require text, set length limits
        render_kw={"placeholder": "Paste news text here..."} # Add placeholder text to the textarea
    )
    submit = SubmitField('Analyze Sentiment')