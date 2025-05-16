import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import User
from app.config import TestingConfig

class TestVisualizationAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        user = User(username='visual', email='visual@example.com')
        user.set_password('vispass')
        db.session.add(user)
        db.session.commit()

        self.client.post('/auth/login', data={
            'username': 'visual',
            'password': 'vispass'
        })

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # 1. Check if the page is accessible and contains all main content
    def test_visualization_page_content(self):
        response = self.client.get('/visualization')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sentiment Analytics Dashboard', response.data)
        self.assertIn(b'Quick Sentiment Overview', response.data)
        self.assertIn(b'Overall Sentiment Breakdown', response.data)
        self.assertIn(b'Sentiment Composition', response.data)
        self.assertIn(b'Weekly Sentiment Trend', response.data)

    # 2. Unauthenticated users should be blocked from access
    def test_visualization_requires_login(self):
        self.client.get('/auth/logout', follow_redirects=True)
        response = self.client.get('/visualization', follow_redirects=False)
        self.assertIn(response.status_code, [302, 401])

if __name__ == '__main__':
    unittest.main()