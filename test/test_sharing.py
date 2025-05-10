"""
Test suite for sharing functionality, including models, routes, and access controls.
"""

import pytest
from flask import url_for
from app.models import User, Result
from datetime import datetime, timezone
import json

pytestmark = pytest.mark.sharing  # Mark all tests in this file as sharing tests

@pytest.fixture
def shared_result(test_user, _db):
    """Create a test result that's shared."""
    result = Result(
        original_text='Shared test content',
        sentiment='Positive',
        author=test_user,
        timestamp=datetime.now(timezone.utc)
    )
    _db.session.add(result)
    _db.session.commit()
    return result

@pytest.fixture
def recipient_user(_db):
    """Create a user who will receive shared content."""
    user = User(username='recipient', email='recipient@example.com')
    user.set_password('recipientpass')
    _db.session.add(user)
    _db.session.commit()
    return user

@pytest.fixture
def recipient_client(client, recipient_user):
    """Create an authenticated client for the recipient user."""
    client.post('/auth/login', data={
        'username': 'recipient',
        'password': 'recipientpass'
    })
    return client

@pytest.mark.parametrize('share_type,expected_status', [
    ('single_user', 302),  # Redirect after successful share
    ('multiple_users', 302),
    ('invalid_user', 200),  # Stay on page with error
])
def test_share_analysis(auth_client, shared_result, _db, share_type, expected_status):
    """Test sharing analysis results with different scenarios."""
    # Create recipient users
    recipients = []
    for i in range(3):
        user = User(username=f'recipient{i}', email=f'recipient{i}@example.com')
        user.set_password('password')
        recipients.append(user)
    _db.session.add_all(recipients)
    _db.session.commit()

    # Prepare share data based on scenario
    if share_type == 'single_user':
        share_data = {'share_with_username': recipients[0].username}
        expected_recipients = [recipients[0]]
    elif share_type == 'multiple_users':
        share_data = {'users_to_share_with': [user.id for user in recipients]}
        expected_recipients = recipients
    else:  # invalid_user
        share_data = {'share_with_username': 'nonexistent_user'}
        expected_recipients = []

    # Attempt to share
    response = auth_client.post(
        f'/results/{shared_result.id}/share',
        data=share_data,
        follow_redirects=True
    )
    assert response.status_code == expected_status

    # Verify sharing status
    for user in expected_recipients:
        assert shared_result in [r for r in user.results_shared_with_me], \
            f"Result not shared with {user.username}"

def test_manage_sharing_permissions(auth_client, shared_result, recipient_user, _db):
    """Test managing sharing permissions."""
    # Initial share
    shared_result.shared_with_recipients.add(recipient_user)
    _db.session.commit()

    # Verify initial share
    assert recipient_user in [u for u in shared_result.shared_with_recipients]

    # Remove sharing
    response = auth_client.post(
        f'/result/{shared_result.id}/manage_sharing',
        data={'users_to_share_with': []}
    )
    assert response.status_code == 302  # Redirect after update

    # Verify sharing removed
    _db.session.refresh(shared_result)
    assert recipient_user not in [u for u in shared_result.shared_with_recipients]

@pytest.mark.parametrize('access_type', ['owner', 'recipient', 'unauthorized'])
def test_shared_result_access(auth_client, recipient_client, client, 
                            shared_result, recipient_user, access_type):
    """Test access controls for shared results."""
    # Setup sharing
    if access_type in ['recipient']:
        shared_result.shared_with_recipients.add(recipient_user)
        shared_result.shared = True  # Mark as shared for public access test
        _db.session.commit()

    # Select appropriate client
    test_client = {
        'owner': auth_client,
        'recipient': recipient_client,
        'unauthorized': client
    }[access_type]

    # Test access to result dashboard
    response = test_client.get(f'/results_dashboard/{shared_result.id}')
    
    if access_type == 'unauthorized':
        assert response.status_code in [302, 403]  # Redirect to login or forbidden
    else:
        assert response.status_code == 200
        assert b'Analysis Results' in response.data

def test_selective_sharing(auth_client, shared_result, _db):
    """Test selective sharing with specific users."""
    # Create multiple potential recipients
    recipients = []
    for i in range(3):
        user = User(username=f'selective{i}', email=f'selective{i}@example.com')
        user.set_password('password')
        recipients.append(user)
    _db.session.add_all(recipients)
    _db.session.commit()

    # Share with specific users
    selected_recipients = recipients[:2]  # Share with first two users
    response = auth_client.post(
        f'/result/{shared_result.id}/manage_sharing',
        data={'users_to_share_with': [user.id for user in selected_recipients]}
    )
    assert response.status_code == 302

    # Verify sharing status
    for user in recipients:
        is_shared = user in selected_recipients
        assert (shared_result in [r for r in user.results_shared_with_me]) == is_shared, \
            f"Incorrect sharing status for {user.username}"

def test_shared_results_list(recipient_client, shared_result, recipient_user, _db):
    """Test listing of shared results."""
    # Share the result
    shared_result.shared_with_recipients.add(recipient_user)
    _db.session.commit()

    # Check shared results page
    response = recipient_client.get('/shared_with_me')
    assert response.status_code == 200
    assert b'Shared With Me' in response.data
    assert shared_result.original_text.encode() in response.data

@pytest.mark.parametrize('scenario', ['remove_user', 'delete_result'])
def test_sharing_cleanup(auth_client, shared_result, recipient_user, _db, scenario):
    """Test cleanup of sharing relationships."""
    # Initial share
    shared_result.shared_with_recipients.add(recipient_user)
    _db.session.commit()

    if scenario == 'remove_user':
        # Delete recipient user
        _db.session.delete(recipient_user)
    else:  # delete_result
        # Delete shared result
        _db.session.delete(shared_result)
    
    _db.session.commit()

    if scenario == 'remove_user':
        # Verify sharing relationship removed
        _db.session.refresh(shared_result)
        assert recipient_user not in [u for u in shared_result.shared_with_recipients]
    else:
        # Verify result removed from shared_results
        _db.session.refresh(recipient_user)
        assert shared_result not in [r for r in recipient_user.results_shared_with_me]
