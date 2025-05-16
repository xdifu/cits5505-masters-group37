import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import User, AnalysisReport
from app.config import TestingConfig

class TestResultsAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.user = User(username='viewer', email='viewer@example.com')
        self.user.set_password('testpass')
        db.session.add(self.user)
        db.session.commit()
 
        self.client.post('/auth/login', data={
            'username': 'viewer',
            'password': 'testpass'
        })

        # Add a historical record
        report = AnalysisReport(user_id=self.user.id, name='Result 1', overall_sentiment_label='Negative')
        db.session.add(report)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    #  1. Logged-in user accesses the results page
    def test_access_results_page(self):
        response = self.client.get('/results')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Result 1', response.data) 

    # 2. Unauthenticated user is denied access
    def test_results_requires_login(self):
        self.client.get('/auth/logout', follow_redirects=True)
        response = self.client.get('/results', follow_redirects=False)
        self.assertIn(response.status_code, [302, 401])

if __name__ == '__main__':
    unittest.main()