import sys
import os
import unittest

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import User, AnalysisReport
from app.config import TestingConfig

class TestResultsAPI(unittest.TestCase):
    def setUp(self):
        # Create a test Flask app instance with TestingConfig
        self.app = create_app(TestingConfig)
        # Disable CSRF protection for easier form testing in unit tests
        self.app.config['WTF_CSRF_ENABLED'] = False
        # Get a test client for making requests
        self.client = self.app.test_client()
        # Create and push an application context
        self.ctx = self.app.app_context()
        self.ctx.push()
        # Create all database tables
        db.create_all()

        # Create a test user
        self.user = User(username='viewer', email='viewer@example.com')
        self.user.set_password('testpass')
        db.session.add(self.user)
        db.session.commit()
 
        # Log in the test user
        self.client.post('/auth/login', data={
            'username': 'viewer',
            'password': 'testpass'
        }, follow_redirects=True) # Ensure session is established

        # Add a historical record for the logged-in user
        report = AnalysisReport(user_id=self.user.id, name='Result 1', overall_sentiment_label='Negative')
        db.session.add(report)
        db.session.commit()

    def tearDown(self):
        # Remove the database session
        db.session.remove()
        # Drop all database tables
        db.drop_all()
        # Pop the application context
        self.ctx.pop()

    # 1. Test that a logged-in user can access the results page and see their reports
    def test_access_results_page(self):
        # Make a GET request to the /results endpoint
        response = self.client.get('/results')
        # Assert that the request was successful (HTTP 200 OK)
        self.assertEqual(response.status_code, 200,
                         "Accessing /results page should return HTTP 200 OK for a logged-in user.")
        # Assert that the user's historical report ('Result 1') is present in the response data
        self.assertIn(b'Result 1', response.data,
                      "The results page should display the user's historical analysis reports.")

    # 2. Test that an unauthenticated user is denied access to the results page
    def test_results_requires_login(self):
        # Log out the current user
        self.client.get('/auth/logout', follow_redirects=True)
        # Attempt to access the /results page without being logged in
        response = self.client.get('/results', follow_redirects=False) # Do not follow redirects to check immediate status
        # Assert that the user is redirected (HTTP 302) or an unauthorized error is returned (HTTP 401)
        self.assertIn(response.status_code, [302, 401],
                      f"Accessing /results without login should redirect (302) or return Unauthorized (401), but got {response.status_code}.")

if __name__ == '__main__':
    unittest.main()