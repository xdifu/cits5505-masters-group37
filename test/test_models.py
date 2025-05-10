import pytest
from app.models import User, Result
from werkzeug.security import check_password_hash
from datetime import datetime, timezone

pytestmark = pytest.mark.models  # Mark all tests in this file as model tests

@pytest.mark.parametrize('user_data', [
    {'username': 'testuser1', 'email': 'test1@example.com', 'password': 'pass1'},
    {'username': 'testuser2', 'email': 'test2@example.com', 'password': 'pass2'},
])
def test_user_creation(_db, user_data):
    """Test successful creation of a User instance with different data."""
    user = User(username=user_data['username'], email=user_data['email'])
    user.set_password(user_data['password'])
    _db.session.add(user)
    _db.session.commit()

    assert user.username == user_data['username'], f"Username mismatch"
    assert user.email == user_data['email'], f"Email mismatch"
    assert user.password_hash is not None, f"Password not hashed"
    assert user.check_password(user_data['password']), f"Password check failed"
    assert not user.check_password('wrongpass'), f"Invalid password check passed"

@pytest.mark.parametrize('sentiment', ['Positive', 'Neutral', 'Negative'])
def test_result_creation(test_user, _db, sentiment):
    """Test successful creation of Result instances with different sentiments."""
    result = Result(
        original_text=f'Test {sentiment.lower()} text',
        sentiment=sentiment,
        author=test_user,
        timestamp=datetime.now(timezone.utc)
    )
    _db.session.add(result)
    _db.session.commit()

    assert result.sentiment == sentiment, f"Sentiment mismatch"
    assert result.author == test_user, f"Author relationship error"
    assert isinstance(result.timestamp, datetime), f"Timestamp type error"

def test_user_relationships(_db, test_user, test_result):
    """Test user relationships with results and shared results."""
    # Verify authored results
    user_results = list(test_user.authored_results)
    assert len(user_results) == 1, "Incorrect number of authored results"
    assert user_results[0] == test_result, "Result not found in authored_results"

    # Test sharing with multiple users
    users = []
    for i in range(3):
        user = User(username=f'user{i}', email=f'user{i}@example.com')
        user.set_password('password')
        users.append(user)
    _db.session.add_all(users)
    _db.session.commit()

    # Share with all users
    for user in users:
        test_result.shared_with_recipients.add(user)
    _db.session.commit()

    # Verify sharing relationships
    for user in users:
        assert test_result in [r for r in user.results_shared_with_me], \
            f"Result not shared with {user.username}"
        assert user in [u for u in test_result.shared_with_recipients], \
            f"User {user.username} not in shared_with_recipients"

def test_cascading_delete(_db, test_user, test_result):
    """Test that deleting a user cascades to their results."""
    result_id = test_result.id
    user_id = test_user.id
    
    _db.session.delete(test_user)
    _db.session.commit()

    assert Result.query.get(result_id) is None, "Result not deleted with user"
    assert User.query.get(user_id) is None, "User not deleted"

@pytest.mark.parametrize('invalid_model,expected_error', [
    (User(), "Missing required fields for User"),
    (Result(), "Missing required fields for Result"),
    (User(username='test'), "Missing email for User"),
    (Result(original_text='test'), "Missing sentiment and author for Result"),
])
def test_model_constraints(_db, invalid_model, expected_error):
    """Test required fields and constraints for models."""
    with pytest.raises(Exception, match=r".*") as excinfo:
        _db.session.add(invalid_model)
        _db.session.commit()
    _db.session.rollback()
    
    assert excinfo.value is not None, f"Expected {expected_error} but no error was raised"
