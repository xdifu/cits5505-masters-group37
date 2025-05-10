import pytest
from unittest.mock import patch, MagicMock
from flask import url_for
from app import create_app, db
from app.models import User, Result
from datetime import datetime, timezone
import json

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
    """Create an authenticated test client."""
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    return client

@pytest.fixture
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

def test_index_route(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the News Sentiment Analyzer' in response.data

def test_analyze_route_unauthorized(client):
    """Test access to analyze route without authentication."""
    response = client.get('/analyze')
    assert response.status_code == 302  # Redirect to login
    assert '/auth/login' in response.location

@patch('app.main.routes.analyze_sentiment')
def test_analyze_route_valid(mock_analyze, auth_client):
    """Test analyze route with valid input."""
    mock_analyze.return_value = 'Positive'
    
    response = auth_client.post('/analyze', data={
        'news_text': 'This is test news content.'
    })
    assert response.status_code == 200
    mock_analyze.assert_called_once_with('This is test news content.')

@patch('app.main.routes.analyze_sentiment')
def test_analyze_route_ajax(mock_analyze, auth_client):
    """Test analyze route with AJAX request."""
    mock_analyze.return_value = 'Negative'
    
    response = auth_client.post('/analyze', 
        data={'news_text': 'Bad news content'},
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['sentiment'] == 'Negative'
    assert 'message' in data

def test_results_route(auth_client, test_result):
    """Test the results route."""
    response = auth_client.get('/results')
    assert response.status_code == 200
    assert b'My Analysis Results' in response.data
    assert b'Positive' in response.data  # From test_result

def test_shared_with_me_route(auth_client, _db, test_result):
    """Test the shared_with_me route."""
    # Create another user and share a result with them
    user2 = User(username='user2', email='user2@example.com')
    user2.set_password('pass2')
    _db.session.add(user2)
    _db.session.commit()
    
    test_result.shared_with_recipients.add(user2)
    _db.session.commit()
    
    # Login as user2
    auth_client.get('/auth/logout')
    auth_client.post('/auth/login', data={
        'username': 'user2',
        'password': 'pass2'
    })
    
    response = auth_client.get('/shared_with_me')
    assert response.status_code == 200
    assert b'Shared With Me' in response.data
    assert b'Test news text' in response.data

def test_manage_sharing_route(auth_client, test_result):
    """Test the manage_sharing route."""
    response = auth_client.get(f'/result/{test_result.id}/manage_sharing')
    assert response.status_code == 200
    assert b'Manage Sharing' in response.data

def test_manage_sharing_unauthorized(client, test_result):
    """Test manage_sharing route without authentication."""
    response = client.get(f'/result/{test_result.id}/manage_sharing')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_manage_sharing_wrong_user(auth_client, _db, test_result):
    """Test manage_sharing route with wrong user."""
    # Create another user
    user2 = User(username='user2', email='user2@example.com')
    user2.set_password('pass2')
    _db.session.add(user2)
    _db.session.commit()
    
    # Login as user2
    auth_client.get('/auth/logout')
    auth_client.post('/auth/login', data={
        'username': 'user2',
        'password': 'pass2'
    })
    
    # Try to manage sharing of test_result (owned by test_user)
    response = auth_client.get(f'/result/{test_result.id}/manage_sharing')
    assert response.status_code == 403

def test_share_analysis_route(auth_client, test_result, _db):
    """Test the share_analysis route."""
    # Create a user to share with
    user2 = User(username='user2', email='user2@example.com')
    user2.set_password('pass2')
    _db.session.add(user2)
    _db.session.commit()
    
    response = auth_client.post(f'/results/{test_result.id}/share', data={
        'share_with_username': 'user2'
    })
    assert response.status_code == 302  # Redirect after successful share
    
    # Verify sharing was successful
    shared_users = [u for u in test_result.shared_with_recipients]
    assert user2 in shared_users

def test_api_filtered_report_data(auth_client, test_result):
    """Test the api_filtered_report_data route."""
    response = auth_client.get(f'/api/filtered_report_data/{test_result.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'news_items' in data
    assert isinstance(data['news_items'], list)

def test_api_filtered_report_data_unauthorized(client, test_result):
    """Test api_filtered_report_data route without authentication."""
    response = client.get(f'/api/filtered_report_data/{test_result.id}')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_analyze_sentiment_error(auth_client):
    """Test analyze route with sentiment analysis error."""
    with patch('app.main.routes.analyze_sentiment') as mock_analyze:
        mock_analyze.return_value = "Error: Analysis failed"
        
        response = auth_client.post('/analyze', data={
            'news_text': 'Test content'
        })
        assert response.status_code == 200
        assert b'Analysis failed' in response.data

def test_results_empty(auth_client):
    """Test results route with no results."""
    response = auth_client.get('/results')
    assert response.status_code == 200
    assert b'No analysis results yet' in response.data
