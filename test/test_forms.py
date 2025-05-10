import pytest
from flask import url_for
from app import create_app, db
from app.models import User
from app.forms import (
    LoginForm, RegistrationForm, AnalysisForm,
    ShareForm, ManageReportSharingForm
)

pytestmark = pytest.mark.forms  # Mark all tests in this file as form tests

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app('testing')
    return app

@pytest.fixture
def _db(app):
    """Create and set up the test database."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def existing_user(_db):
    """Create a test user in the database."""
    user = User(username='existinguser', email='existing@example.com')
    user.set_password('password123')
    _db.session.add(user)
    _db.session.commit()
    return user

@pytest.mark.parametrize('form_data,expected_valid', [
    (
        {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'password2': 'password123'
        },
        True
    ),
    (
        {
            'username': 'existinguser',  # Existing username
            'email': 'new@example.com',
            'password': 'password123',
            'password2': 'password123'
        },
        False
    ),
    (
        {
            'username': 'newuser',
            'email': 'invalid-email',  # Invalid email
            'password': 'password123',
            'password2': 'password123'
        },
        False
    ),
    (
        {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'password2': 'different123'  # Mismatched passwords
        },
        False
    ),
])
def test_registration_form(app, existing_user, form_data, expected_valid):
    """Test RegistrationForm validation with various scenarios."""
    with app.test_request_context():
        form = RegistrationForm(**form_data)
        assert form.validate() == expected_valid

        if not expected_valid:
            if form_data['username'] == 'existinguser':
                assert 'Please use a different username' in form.username.errors
            elif 'invalid-email' in form_data['email']:
                assert any('Invalid email address' in error for error in form.email.errors)
            elif form_data['password'] != form_data['password2']:
                assert 'Passwords must match' in form.password2.errors

@pytest.mark.parametrize('form_data,expected_valid,error_message', [
    (
        {'username': 'testuser', 'password': 'password123', 'remember_me': True},
        True,
        None
    ),
    (
        {'username': '', 'password': 'password123'},  # Missing username
        False,
        'This field is required'
    ),
    (
        {'username': 'testuser', 'password': ''},  # Missing password
        False,
        'This field is required'
    ),
])
def test_login_form(app, form_data, expected_valid, error_message):
    """Test LoginForm validation with various scenarios."""
    with app.test_request_context():
        form = LoginForm(**form_data)
        assert form.validate() == expected_valid
        
        if error_message:
            if 'username' not in form_data or not form_data['username']:
                assert error_message in form.username.errors
            if 'password' not in form_data or not form_data['password']:
                assert error_message in form.password.errors

@pytest.mark.parametrize('news_text,expected_valid,error_type', [
    ('This is a valid news article.', True, None),
    ('', False, 'required'),  # Empty text
    ('x' * 10001, False, 'length'),  # Too long
])
def test_analysis_form(app, news_text, expected_valid, error_type):
    """Test AnalysisForm validation with various scenarios."""
    with app.test_request_context():
        form = AnalysisForm(news_text=news_text)
        assert form.validate() == expected_valid

        if not expected_valid:
            if error_type == 'required':
                assert 'This field is required' in form.news_text.errors
            elif error_type == 'length':
                assert any('length should be between 1 and 10000' in error 
                         for error in form.news_text.errors)

def test_share_form_validation(app):
    """Test ShareForm validation."""
    with app.test_request_context():
        # Test valid username
        form = ShareForm(share_with_username='testuser')
        assert form.validate()

        # Test empty username
        form = ShareForm(share_with_username='')
        assert not form.validate()
        assert 'This field is required' in form.share_with_username.errors

def test_manage_sharing_form(app, _db):
    """Test ManageReportSharingForm initialization and choices."""
    # Create test users
    users = []
    for i in range(3):
        user = User(username=f'user{i}', email=f'user{i}@example.com')
        user.set_password('password123')
        users.append(user)
    _db.session.add_all(users)
    _db.session.commit()

    with app.test_request_context():
        # Test form with first user as current user
        form = ManageReportSharingForm(current_user_id=users[0].id)
        
        # Verify choices
        assert len(form.users_to_share_with.choices) == 2
        assert all(isinstance(choice[0], int) for choice in form.users_to_share_with.choices)
        assert all(isinstance(choice[1], str) for choice in form.users_to_share_with.choices)
        assert users[0].id not in [choice[0] for choice in form.users_to_share_with.choices]
        
        # Test form submission
        form = ManageReportSharingForm(
            current_user_id=users[0].id,
            users_to_share_with=[users[1].id]
        )
        assert form.validate()
