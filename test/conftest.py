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
    """Create and set up the test database for each test function.
    This ensures each test runs with a clean database state.
    """
    with app.app_context():
        # Create all tables directly instead of using migrations
        db.create_all()
        
        yield db # Provide the db session to the tests

        # After the test, clear the session and drop all tables
        db.session.remove()
        db.drop_all() # This ensures a completely clean database for the next test

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
def test_analysis_report(test_user, _db):
    """Create a test analysis report."""
    report = AnalysisReport(
        name='Test Report',
        author=test_user,
        timestamp=datetime.now(timezone.utc),
        overall_sentiment_label='Positive',
        overall_sentiment_score=0.8,
        aggregated_intents_json='{"News Report": 1.0}',
        aggregated_keywords_json='[{"text": "test", "count": 1, "avg_sentiment": 0.8}]',
        sentiment_trend_json='{"overall": [{"date": "2024-01-01", "score": 0.8}]}'
    )
    _db.session.add(report)
    _db.session.commit()
    return report
