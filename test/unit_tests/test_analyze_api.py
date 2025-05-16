import sys
import os
import unittest

# 添加根目录
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import User
from app.config import TestingConfig

class TestAnalyzeAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for easier testing
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()

        self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # 1. Normal text submission
    def test_valid_analysis(self):
        response = self.client.post('/analyze', data={
            'content': 'The weather is great and I feel happy.'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'sentiment', response.data) 

    # 2. Access without login
    def test_analyze_requires_login(self):
        self.client.get('/auth/logout', follow_redirects=True)
        response = self.client.post('/analyze', data={
            'content': 'hello'
        }, follow_redirects=False)
        self.assertIn(response.status_code, [302, 401]) 

if __name__ == '__main__':
    unittest.main()