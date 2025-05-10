import pytest
from app import create_app, db
from app.models import User, Result
from datetime import datetime, timezone

@pytest.fixture(scope='session')
def app():
    """Create and configure a test app instance."""
    app = create_app('testing')
    return app

@pytest.fixture(scope='function')
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture(scope='function')
def _db(app):
    """Create and set up the test database."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

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
    result = Result(
        original_text='Test news text',
        sentiment='Positive',
        author=test_user,
        timestamp=datetime.now(timezone.utc)
    )
    _db.session.add(result)
    _db.session.commit()
    return result
