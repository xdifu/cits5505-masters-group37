import sys
import os
import unittest
from werkzeug.datastructures import MultiDict

# 添加项目根目录到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.forms import LoginForm
from app.config import TestingConfig

class TestLoginForm(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    #  1. Both username and password are correct → Pass
    def test_valid_login_form(self):
        form = LoginForm(
            formdata=MultiDict({
                'username': 'validuser',
                'password': 'securepass'
            }),
            meta={'csrf': False}
        )
        self.assertTrue(form.validate())

    #  2. Username is empty → Error message
    def test_missing_username(self):
        form = LoginForm(
            formdata=MultiDict({
                'username': '',
                'password': 'securepass'
            }),
            meta={'csrf': False}
        )
        self.assertFalse(form.validate())
        self.assertIn('This field is required.', str(form.errors.get('username')))

    #  3. Password is empty → Error message
    def test_missing_password(self):
        form = LoginForm(
            formdata=MultiDict({
                'username': 'user1',
                'password': ''
            }),
            meta={'csrf': False}
        )
        self.assertFalse(form.validate())
        self.assertIn('This field is required.', str(form.errors.get('password')))

if __name__ == '__main__':
    unittest.main()