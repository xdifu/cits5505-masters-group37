import sys
import os
import unittest
from werkzeug.datastructures import MultiDict

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.forms import LoginForm
from app.config import TestingConfig

class TestLoginForm(unittest.TestCase):
    def setUp(self):
        # Create a test Flask app instance with TestingConfig
        self.app = create_app(TestingConfig)
        # Create and push an application context
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        # Pop the application context
        self.ctx.pop()

    # 1. Test that the form validates successfully when both username and password are provided
    def test_valid_login_form(self):
        # Create a form instance with valid data
        form = LoginForm(
            formdata=MultiDict({
                'username': 'validuser',
                'password': 'securepassword'
            }),
            meta={'csrf': False} # Disable CSRF for unit testing forms directly
        )
        # Assert that the form validation passes
        self.assertTrue(form.validate(),
                        "Form should be valid when all required fields are provided correctly.")

    # 2. Test that the form shows an error message when the username is missing
    def test_missing_username(self):
        # Create a form instance with a missing username
        form = LoginForm(
            formdata=MultiDict({
                'username': '',
                'password': 'securepassword'
            }),
            meta={'csrf': False}
        )
        # Assert that the form validation fails
        self.assertFalse(form.validate(),
                         "Form should be invalid when username is missing.")
        # Assert that the correct error message is present for the username field
        self.assertIn('This field is required.', str(form.errors.get('username')),
                      "Error message for missing username is incorrect or not present.")

    # 3. Test that the form shows an error message when the password is empty
    def test_missing_password(self):
        # Create a form instance with a missing password
        form = LoginForm(
            formdata=MultiDict({
                'username': 'testuser',
                'password': ''
            }),
            meta={'csrf': False}
        )
        # Assert that the form validation fails
        self.assertFalse(form.validate(),
                         "Form should be invalid when password is missing.")
        # Assert that the correct error message is present for the password field
        self.assertIn('This field is required.', str(form.errors.get('password')),
                      "Error message for missing password is incorrect or not present.")

if __name__ == '__main__':
    unittest.main()