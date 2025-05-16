import sys
import os
import unittest

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import User
from app.config import TestingConfig

class TestAnalyzeAPI(unittest.TestCase):
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
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()

        # Log in the test user
        self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True) # Ensure session is established

    def tearDown(self):
        # Remove the database session
        db.session.remove()
        # Drop all database tables
        db.drop_all()
        # Pop the application context
        self.ctx.pop()

    # 1. Test normal text submission for analysis by a logged-in user
    def test_valid_analysis(self):
        # Simulate a POST request to the /analyze endpoint with valid data
        response = self.client.post('/analyze', data={
            'content': 'The weather is great and I feel happy.'
        }, follow_redirects=True) # Follow redirects to get the final page
        # Assert that the request was successful (HTTP 200 OK)
        self.assertEqual(response.status_code, 200,
                         "Analysis submission should return HTTP 200 OK.")
        # Assert that the response data contains the word 'sentiment' (or a more specific result indicator)
        self.assertIn(b'sentiment', response.data.lower(), # Check in lowercase for robustness
                      "Response data should contain analysis results, including 'sentiment'.")

    # 2. Test that accessing the /analyze endpoint requires login
    def test_analyze_requires_login(self):
        # Log out the current user
        self.client.get('/auth/logout', follow_redirects=True)
        # Attempt to POST to /analyze without being logged in
        response = self.client.post('/analyze', data={
            'content': 'This is a test text that should not be processed.'
        }, follow_redirects=False) # Do not follow redirects to check the immediate response
        # Assert that the user is redirected (HTTP 302) or an unauthorized error is returned (HTTP 401)
        self.assertIn(response.status_code, [302, 401],
                      "Accessing /analyze without login should redirect to login (302) or return Unauthorized (401).")

if __name__ == '__main__':
    unittest.main()