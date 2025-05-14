import pytest
from app import create_app, db
from app.models import User, AnalysisReport
from config import TestingConfig
from flask_migrate import upgrade, downgrade
from datetime import datetime, timezone

@pytest.fixture(scope='session')
def app():
    """Create and configure a test app instance."""
    app = create_app(TestingConfig)
    return app

@pytest.fixture(scope='function')
def client(app, _db):
    """Create a test client."""
    return app.test_client()

@pytest.fixture(scope='function')
def _db(app):
    """Create and set up the test database using migrations for each test function.
    This ensures each test runs with a clean database state.
    """
    with app.app_context():
        # Apply all migrations to set up the schema
        upgrade() 
        
        yield db # Provide the db session to the tests

        # After the test, clear the session and drop all tables
        # Downgrading to base is an alternative if you want to test migrations specifically
        # but drop_all is simpler for a clean slate with in-memory SQLite.
        db.session.remove()
        db.drop_all() # This ensures a completely clean database for the next test
        # Alternatively, to revert all migrations:
        # downgrade(revision='base')

@pytest.fixture(scope='function')
def test_user(_db):
    """Create a test user."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpass')
    _db.session.add(user)
    _db.session.commit()
    return user

@pytest.fixture(scope='function')
def auth_client(client, test_user):
    """Create an authenticated test client."""
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    return client

@pytest.fixture(scope='function')
def test_result(test_user, _db):
    """Create a test result."""
    result = AnalysisReport(
        original_text='Test news text',
        sentiment='Positive',
        author=test_user,
        timestamp=datetime.now(timezone.utc)
    )
    _db.session.add(result)
    _db.session.commit()
    return result
