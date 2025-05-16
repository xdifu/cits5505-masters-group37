import sys
import os
import unittest

# 添加项目根目录到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import User
from app.config import TestingConfig

class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    #  1. Test that the password hash is not plain text
    def test_password_hashing(self):
        user = User(username='tester')
        user.set_password('cat123')
        self.assertNotEqual(user.password_hash, 'cat123')

    # 2. Test password verification success
    def test_check_correct_password(self):
        user = User(username='tester')
        user.set_password('cat123')
        self.assertTrue(user.check_password('cat123'))

    # 3. Test password verification failure
    def test_check_wrong_password(self):
        user = User(username='tester')
        user.set_password('cat123')
        self.assertFalse(user.check_password('dog456'))

if __name__ == '__main__':
    unittest.main()