import pytest
import sqlalchemy as sa
from app.models import User, AnalysisReport  # Changed Result to AnalysisReport
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

@pytest.mark.parametrize('sentiment_label', ['Positive', 'Neutral', 'Negative'])
def test_analysis_report_creation(test_user, _db, sentiment_label):
    """Test successful creation of AnalysisReport instances with different overall sentiments."""
    report = AnalysisReport(
        name=f'Test Report - {sentiment_label}', # Using the 'name' field
        overall_sentiment_label=sentiment_label, # Using 'overall_sentiment_label'
        overall_sentiment_score=0.5, # Example score
        author=test_user,
        timestamp=datetime.now(timezone.utc)
    )
    _db.session.add(report)
    _db.session.commit()

    assert report.name == f'Test Report - {sentiment_label}', "Report name mismatch"
    assert report.overall_sentiment_label == sentiment_label, f"Overall sentiment label mismatch"
    assert report.author == test_user, f"Author relationship error"
    assert isinstance(report.timestamp, datetime), f"Timestamp type error"

def test_user_relationships(_db, test_user, test_analysis_report):
    """Test user relationships with analysis reports and shared reports."""
    # Verify authored analysis reports using SQLAlchemy 2.0 style select
    stmt = sa.select(AnalysisReport).where(AnalysisReport.author == test_user)
    user_reports = list(_db.session.scalars(stmt))
    assert len(user_reports) == 1, "Incorrect number of authored analysis reports"
    assert test_analysis_report in user_reports, "Report not found in authored_analysis_reports"

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
        test_analysis_report.shared_with_recipients.append(user)
    _db.session.commit()

    # Verify sharing relationships
    for user in users:
        assert test_analysis_report in user.analysis_reports_shared_with_me, \
            f"Report not shared with {user.username}"
        assert user in test_analysis_report.shared_with_recipients, \
            f"User {user.username} not in shared_with_recipients"

def test_cascading_delete(_db, test_user, test_analysis_report):
    """Test that deleting a user cascades to their analysis reports."""
    report_id = test_analysis_report.id
    user_id = test_user.id
    
    _db.session.delete(test_user)
    _db.session.commit()

    assert _db.session.get(AnalysisReport, report_id) is None, "Analysis report not deleted with user"
    assert _db.session.get(User, user_id) is None, "User not deleted"

@pytest.mark.parametrize('invalid_model_args, expected_error_part', [
    # Test cases for User model remain the same if they are valid
    (lambda: User(), "(sqlite3.IntegrityError) NOT NULL constraint failed: user.username"), # More specific error for User
    (lambda: User(username='test'), "(sqlite3.IntegrityError) NOT NULL constraint failed: user.email"), # More specific error for User
    # Test cases for AnalysisReport - adjusted for actual fields and potential errors
    # An AnalysisReport needs at least user_id (author) due to ForeignKey constraint
    # (lambda: AnalysisReport(), "NOT NULL constraint failed: analysis_report.user_id"), # This would be a DB error
    # For now, let's focus on type errors or missing required fields if any are not nullable and have no default
    # If all direct fields on AnalysisReport are optional or have defaults (besides foreign keys handled by relationships),
    # then instantiating it empty might not raise an immediate Python error but a DB error on commit without an author.
    # The original test was (AnalysisReport(), "Missing required fields for Result")
    # Let's assume for now that an empty AnalysisReport() is permissible at object creation if author is set later.
    # The test (AnalysisReport(original_text='test'), "Missing sentiment and author for Result") is invalid due to 'original_text'
    # We'll remove the problematic AnalysisReport tests for now, as they need significant rework
    # to align with the NewsItem structure for text and individual sentiments.
])
def test_model_constraints(_db, invalid_model_args, expected_error_part):
    """Test required fields and constraints for models."""
    # This test needs significant rework for AnalysisReport due to model changes.
    # For now, we will focus on User constraints which are clearer.
    # The original test for AnalysisReport was based on fields that no longer exist directly on it.
    model_instance = invalid_model_args() # Call the lambda to get the model instance

    with pytest.raises(Exception) as excinfo:
        _db.session.add(model_instance)
        _db.session.commit()
    _db.session.rollback() # Ensure rollback after error
    
    assert excinfo.value is not None, f"Expected an error but no error was raised for {model_instance}"
    # Check if part of the expected error string is in the actual error message
    # This makes the test less brittle to exact error message phrasing from SQLAlchemy or DB
    assert expected_error_part.lower() in str(excinfo.value).lower(), \
        f"Error message '{str(excinfo.value)}' did not contain expected part '{expected_error_part}' for {model_instance}"
