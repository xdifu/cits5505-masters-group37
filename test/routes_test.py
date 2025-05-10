"""
Integration test for the routes related to selective sharing.

This script tests:
1. Creating users and results
2. The share_analysis route for sharing with specific users
3. The shared_with_me route for viewing shared results
4. The manage_sharing route for managing multiple sharing recipients
"""

import unittest
from app import create_app, db
from app.models import User, AnalysisReport, NewsItem # Assuming AnalysisReport and NewsItem are the correct model names
from flask import url_for
from datetime import datetime

class SharingIntegrationTests(unittest.TestCase):
    """
    Integration tests for the selective sharing functionality.
    This class tests:
    1. Creating users and analysis reports.
    2. Sharing an analysis report with specific users.
    3. Viewing reports shared with the current user.
    4. Access control for viewing reports (shared vs. not shared).
    5. Managing sharing recipients (e.g., revoking access).
    """

    def setUp(self):
        """
        Set up the test environment.
        This method is called before each test.
        It creates a new application instance for testing, initializes the database,
        and creates a test client.
        """
        self.app = create_app(config_name='testing') # Use 'testing' config_name
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all() # Create tables in the in-memory database
        self.client = self.app.test_client()

        # Create test users
        self.user1 = User(username='user1', email='user1@example.com')
        self.user1.set_password('password123')
        self.user2 = User(username='user2', email='user2@example.com')
        self.user2.set_password('password123')
        self.user3 = User(username='user3', email='user3@example.com')
        self.user3.set_password('password123')
        db.session.add_all([self.user1, self.user2, self.user3])
        db.session.commit()

        # Create a test analysis report owned by user1
        self.report1 = AnalysisReport(name='Test Report 1', user_id=self.user1.id)
        # Add a NewsItem to the report to make 'results_exist' true in the template
        news_item1 = NewsItem(
            original_text="This is a test news item for report 1.",
            sentiment_label="Neutral",
            sentiment_score=0.0,
            publication_date=datetime.utcnow(),
            analysis_report=self.report1
        )
        db.session.add_all([self.user1, self.user2, self.user3, self.report1, news_item1])
        db.session.commit()

    def tearDown(self):
        """
        Clean up the test environment.
        This method is called after each test.
        It removes the database session and drops all tables.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        """Helper method to log in a user."""
        return self.client.post(url_for('auth.login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """Helper method to log out a user."""
        return self.client.get(url_for('auth.logout'), follow_redirects=True)

    def test_owner_can_view_own_report(self):
        """Test that the owner of a report can view it."""
        self.login('user1', 'password123')
        response = self.client.get(url_for('main.results_dashboard', report_id=self.report1.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Report 1', response.data)
        self.logout()

    def test_share_report_and_recipient_can_view(self):
        """Test sharing a report with another user and verify recipient can view it."""
        self.login('user1', 'password123')
        # Share report1 with user2
        # Corrected endpoint from 'main.share_analysis' to 'main.share_report'
        share_url = url_for('main.share_report', report_id=self.report1.id)
        response = self.client.post(share_url, data=dict(
            share_with_username='user2' # This assumes the form field in share_report.html is 'share_with_username'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Assuming redirect to a success page or dashboard
        # Check if 'Successfully shared' or similar message is present if applicable
        # self.assertIn(b'Report shared successfully', response.data) # Example assertion
        self.logout()

        # User2 (recipient) tries to view the report
        self.login('user2', 'password123')
        response = self.client.get(url_for('main.results_dashboard', report_id=self.report1.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Report 1', response.data)
        self.logout()

    def test_unauthorized_user_cannot_view_report(self):
        """Test that a user not shared with cannot view the report."""
        self.login('user3', 'password123') # User3 was not shared with
        response = self.client.get(url_for('main.results_dashboard', report_id=self.report1.id))
        # Expecting a 403 Forbidden or redirect to an error page/login page
        # If it redirects to login for unauthorized, status might be 302 then 200 for login page
        # For simplicity, let's assume it's a 403 or the content is not there.
        # A more robust check would be to ensure the report content is NOT present,
        # or a specific "access denied" message is shown.
        self.assertNotIn(b'Test Report 1', response.data)
        # Or, if a 403 is returned:
        # self.assertEqual(response.status_code, 403)
        self.logout()

    def test_view_shared_with_me_page(self):
        """Test the 'shared_with_me' page lists reports shared with the current user."""
        # User1 shares report1 with User2
        self.login('user1', 'password123')
        # Corrected endpoint from 'main.share_analysis' to 'main.share_report'
        share_url = url_for('main.share_report', report_id=self.report1.id)
        self.client.post(share_url, data=dict(share_with_username='user2'), follow_redirects=True)
        self.logout()

        # User2 logs in and checks their 'shared_with_me' page
        self.login('user2', 'password123')
        response = self.client.get(url_for('main.shared_with_me'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Report 1', response.data) # Check if report1 is listed
        self.logout()

        # User3 logs in and checks their 'shared_with_me' page (should be empty or not list report1)
        self.login('user3', 'password123')
        response = self.client.get(url_for('main.shared_with_me'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Test Report 1', response.data)
        self.logout()

    def test_manage_sharing_revoke_access(self):
        """Test revoking access to a shared report via manage_sharing."""
        # User1 shares report1 with User2
        self.login('user1', 'password123')
        # Corrected endpoint from 'main.share_analysis' to 'main.share_report'
        share_url = url_for('main.share_report', report_id=self.report1.id)
        self.client.post(share_url, data=dict(share_with_username='user2'), follow_redirects=True)
        
        # User1 revokes access for User2 using the manage_sharing route
        # This assumes 'manage_sharing' takes a list of user IDs or usernames to *keep* shared.
        # Or, it might take a list of users to remove. The exact mechanism depends on implementation.
        # For this example, let's assume we POST to remove a specific user.
        # The form field 'users_to_remove' or similar would be needed.
        # Or, if 'manage_sharing' form submits a list of *current* recipients,
        # submitting an empty list or a list without user2 would revoke access.
        
        # Let's assume manage_sharing allows POSTing a list of usernames to share with.
        # To revoke from user2, user1 would submit an empty list or a list without user2.
        manage_url = url_for('main.manage_sharing', report_id=self.report1.id)
        # Example: Revoke by submitting an empty list of users to share with
        # The form field name 'users_to_share_with' is from the conversation summary.
        response = self.client.post(manage_url, data=dict(
            users_to_share_with=[] # Empty list, or list excluding user2
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Assuming success
        self.logout()

        # User2 tries to view the report again - should fail
        self.login('user2', 'password123')
        response = self.client.get(url_for('main.results_dashboard', report_id=self.report1.id))
        self.assertNotIn(b'Test Report 1', response.data) # Or check for 403
        self.logout()

if __name__ == '__main__':
    unittest.main(verbosity=2)
