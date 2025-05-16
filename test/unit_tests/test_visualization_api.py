import sys
import os
import unittest

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import User
from app.config import TestingConfig

class TestVisualizationAPI(unittest.TestCase):
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

        # Create and log in a test user
        user = User(username='visual', email='visual@example.com')
        user.set_password('vispass')
        db.session.add(user)
        db.session.commit()

        self.client.post('/auth/login', data={
            'username': 'visual',
            'password': 'vispass'
        }, follow_redirects=True) # Ensure session is established

    def tearDown(self):
        # Remove the database session
        db.session.remove()
        # Drop all database tables
        db.drop_all()
        # Pop the application context
        self.ctx.pop()

    # 1. Check if the page is accessible and contains all main content elements
    def test_visualization_page_content(self):
        # Make a GET request to the /visualization endpoint
        response = self.client.get('/visualization')
        # Assert that the request was successful (HTTP 200 OK)
        self.assertEqual(response.status_code, 200,
                         "Accessing /visualization page should return HTTP 200 OK for a logged-in user.")
        # Assert that key textual elements are present in the response data
        self.assertIn(b'Sentiment Analytics Dashboard', response.data,
                      "Page should contain the main title 'Sentiment Analytics Dashboard'.")
        self.assertIn(b'Quick Sentiment Overview', response.data,
                      "Page should contain the section 'Quick Sentiment Overview'.")
        self.assertIn(b'Overall Sentiment Breakdown', response.data,
                      "Page should contain the section 'Overall Sentiment Breakdown'.")
        self.assertIn(b'Sentiment Composition', response.data,
                      "Page should contain the section 'Sentiment Composition'.")
        self.assertIn(b'Weekly Sentiment Trend', response.data,
                      "Page should contain the section 'Weekly Sentiment Trend'.")

    # 2. Test that unauthenticated users are blocked from accessing the visualization page
    def test_visualization_requires_login(self):
        # Log out the current user
        self.client.get('/auth/logout', follow_redirects=True)
        # Attempt to access the /visualization page without being logged in
        response = self.client.get('/visualization', follow_redirects=False) # Do not follow redirects to check immediate status
        # Assert that the user is redirected (HTTP 302) or an unauthorized error is returned (HTTP 401)
        self.assertIn(response.status_code, [302, 401],
                      f"Accessing /visualization without login should redirect (302) or return Unauthorized (401), but got {response.status_code}.")

if __name__ == '__main__':
    unittest.main()