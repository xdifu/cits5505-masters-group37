import sys
import os
import unittest

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import User
from app.config import TestingConfig

class TestUserModel(unittest.TestCase):
    def setUp(self):
        # Create a test Flask app instance with TestingConfig
        self.app = create_app(TestingConfig)
        # Create and push an application context
        self.ctx = self.app.app_context()
        self.ctx.push()
        # Create all database tables
        db.create_all()

        # Create a common user instance for use in tests
        self.user = User(username='tester')
        self.user.set_password('cat123')
        # Note: For these specific tests, adding the user to db.session and committing
        # is not strictly necessary as we are testing model methods on an in-memory object.
        # If tests required database interaction with this user, you would add:
        # db.session.add(self.user)
        # db.session.commit()

    def tearDown(self):
        # Remove the database session
        db.session.remove()
        # Drop all database tables
        db.drop_all()
        # Pop the application context
        self.ctx.pop()

    # 1. Test that the password hash is not plain text
    def test_password_hashing(self):
        # Assert that the stored password_hash is not equal to the original plain text password
        self.assertNotEqual(self.user.password_hash, 'cat123',
                            "Password hash should not be the plain text password 'cat123'.")

    # 2. Test password verification success
    def test_check_correct_password(self):
        # Assert that check_password returns True for the correct password
        self.assertTrue(self.user.check_password('cat123'),
                        "check_password should return True for the correct password 'cat123'.")

    # 3. Test password verification failure
    def test_check_wrong_password(self):
        # Assert that check_password returns False for an incorrect password
        self.assertFalse(self.user.check_password('dog456'),
                         "check_password should return False for the incorrect password 'dog456'.")

if __name__ == '__main__':
    unittest.main()