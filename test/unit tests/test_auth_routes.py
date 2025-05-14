import pytest
from flask import url_for
from app import create_app, db
from app.models import User
from flask_login import current_user

pytestmark = pytest.mark.auth  # Mark all tests in this file as auth tests

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
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def test_user(_db):
    """Create a test user."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpass')
    _db.session.add(user)
    _db.session.commit()
    return user

@pytest.fixture
def auth_client(client, test_user):
    """Create an authenticated client."""
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    return client

@pytest.mark.parametrize('endpoint', [
    '/auth/login',
    '/auth/register'
])
def test_auth_pages_load(client, endpoint):
    """Test that authentication pages load correctly."""
    response = client.get(endpoint)
    assert response.status_code == 200, f"Failed to load {endpoint}"
    
    expected_content = {
        '/auth/login': [b'Sign In', b'Username', b'Password'],
        '/auth/register': [b'Register', b'Username', b'Email', b'Password', b'Repeat Password']
    }
    
    for content in expected_content[endpoint]:
        assert content in response.data, f"Missing content {content} in {endpoint}"

@pytest.mark.parametrize('credentials,expected_message', [
    ({'username': 'testuser', 'password': 'testpass'}, b'Welcome'),
    ({'username': 'testuser', 'password': 'wrongpass'}, b'Invalid username or password'),
    ({'username': 'nonexistent', 'password': 'testpass'}, b'Invalid username or password'),
])
def test_login_scenarios(client, test_user, credentials, expected_message):
    """Test various login scenarios with different credentials."""
    response = client.post('/auth/login', data={
        'username': credentials['username'],
        'password': credentials['password'],
        'remember_me': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert expected_message in response.data

    # Check session state
    with client.session_transaction() as session:
        is_authenticated = '_user_id' in session
        should_be_authenticated = credentials == {'username': 'testuser', 'password': 'testpass'}
        assert is_authenticated == should_be_authenticated, \
            f"Unexpected authentication state. Expected: {should_be_authenticated}, Got: {is_authenticated}"

@pytest.mark.parametrize('remember', [True, False])
def test_remember_me(client, test_user, remember):
    """Test remember me functionality with both states."""
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass',
        'remember_me': remember
    })
    
    has_remember_token = any(cookie.name == 'remember_token' for cookie in client.cookie_jar)
    assert has_remember_token == remember, \
        f"Remember token {'missing' if remember else 'present'} when remember_me is {remember}"

@pytest.mark.parametrize('registration_data,expected_message', [
    ({
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass123',
        'password2': 'newpass123'
    }, b'Congratulations, you are now a registered user!'),
    ({
        'username': 'testuser',  # Existing username
        'email': 'another@example.com',
        'password': 'pass123',
        'password2': 'pass123'
    }, b'Please use a different username'),
    ({
        'username': 'newuser',
        'email': 'test@example.com',  # Existing email
        'password': 'pass123',
        'password2': 'pass123'
    }, b'Please use a different email address'),
    ({
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'pass123',
        'password2': 'different123'  # Mismatched passwords
    }, b'Passwords must match'),
    ({
        'username': 'newuser',
        'email': 'invalid-email',  # Invalid email
        'password': 'pass123',
        'password2': 'pass123'
    }, b'Invalid email address'),
    ({
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'short',  # Short password
        'password2': 'short'
    }, b'Field must be at least 6 characters long'),
])
def test_registration_scenarios(client, test_user, _db, registration_data, expected_message):
    """Test various registration scenarios."""
    response = client.post('/auth/register', 
        data=registration_data, 
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert expected_message in response.data

    # Verify database state for successful registration
    if b'Congratulations' in expected_message:
        user = User.query.filter_by(username=registration_data['username']).first()
        assert user is not None, "User not created in database"
        assert user.email == registration_data['email'], "Email mismatch in database"

@pytest.mark.parametrize('endpoint', ['/auth/login', '/auth/register'])
def test_authenticated_user_redirect(auth_client, endpoint):
    """Test that authenticated users are redirected from auth pages."""
    response = auth_client.get(endpoint, follow_redirects=True)
    assert response.status_code == 200
    assert b'You are already logged in' in response.data

def test_logout(auth_client):
    """Test logout functionality."""
    response = auth_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    
    with auth_client.session_transaction() as session:
        assert '_user_id' not in session, "User still in session after logout"
        
    # Verify redirected to login page
    response = auth_client.get('/analyze')
    assert response.status_code == 302
    assert '/auth/login' in response.location
