\
import unittest
from flask import Flask, render_template_string, render_template
from jinja2.exceptions import TemplateSyntaxError
from datetime import datetime, timezone
import json

# Mock objects to simulate database models
class MockUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username

class MockNewsItem:
    def __init__(self, id, original_text, sentiment_label="Neutral", sentiment_score=0.0, publication_date=None, intents_json="[]", keywords_json="[]"):
        self.id = id
        self.original_text = original_text
        self.sentiment_label = sentiment_label
        self.sentiment_score = sentiment_score
        self.publication_date = publication_date or datetime.now(timezone.utc)
        self.intents_json = intents_json
        self.keywords_json = keywords_json
        # self.intents = json.loads(intents_json) # For direct access if needed by template logic
        # self.keywords = json.loads(keywords_json) # For direct access if needed by template logic

    def to_dict(self): # Add a to_dict method
        return {
            'id': self.id,
            'original_text': self.original_text,
            'sentiment_label': self.sentiment_label,
            'sentiment_score': self.sentiment_score,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'intents': json.loads(self.intents_json),
            'keywords': json.loads(self.keywords_json)
        }

class MockAnalysisReport:
    def __init__(self, id, name, user_id, overall_sentiment_label="Neutral", overall_sentiment_score=0.0):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.timestamp = datetime.now(timezone.utc)
        self.author = MockUser(user_id, "testuser")
        self.news_items = []
        self.shared_with_recipients = []
        self.shared = False
        self.overall_sentiment_label = overall_sentiment_label
        self.overall_sentiment_score = overall_sentiment_score
        self.aggregated_intents_json = "{}"
        self.aggregated_keywords_json = "[]"
        self.sentiment_trend_json = "{}"

    def add_news_item(self, item):
        self.news_items.append(item)

# Minimal Flask app for testing
app = Flask(__name__)
app.config['TESTING'] = True
# Add a dummy 'from_json' filter if your template uses it and it's custom
# For this test, we'll assume 'to_dict' is the primary mechanism
# and 'from_json' might not be hit if 'to_dict' is used.
# If 'from_json' is a standard Jinja filter or part of an extension, it should be fine.
# For now, we'll focus on the map(attribute=...) part.

# If 'from_json' is a custom filter, it needs to be registered:
# def from_json_filter(value):
# try:
# return json.loads(value)
# except (TypeError, json.JSONDecodeError):
# return None
# app.jinja_env.filters['from_json'] = from_json_filter


class TestJinjaSyntax(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

        # Create mock data
        self.report = MockAnalysisReport(id=1, name="Test Report", user_id=1)
        self.report.add_news_item(MockNewsItem(id=1, original_text="News 1", intents_json='["News Report"]', keywords_json='["economy"]'))
        self.report.add_news_item(MockNewsItem(id=2, original_text="News 2", intents_json='["Opinion"]', keywords_json='["politics"]'))

        # Mock data for other parts of the template to avoid unrelated errors
        self.top_5_intents = {"News Report": 60, "Opinion": 40}
        self.sentiment_trend_chart_data = {"labels": ["2023-01-01"], "datasets": []}
        self.top_20_keywords_data = [{"text": "economy", "value": 10}]
        self.entity_overview_score = 0.5


    def tearDown(self):
        self.app_context.pop()

    def test_render_results_dashboard_original_syntax_fails(self):
        # This test expects the TemplateSyntaxError with the original problematic code.
        # We need to simulate the template content that causes the error.
        # The actual file 'results_dashboard.html' will be used by Flask's render_template.
        # For this test to be effective, the 'results_dashboard.html' must currently contain the error.

        # Define a route that uses the template
        @app.route('/test_dashboard_render_fail')
        def test_dashboard_render_fail():
            return render_template('results_dashboard.html', # This will load the actual file
                                   report=self.report,
                                   results=self.report, # Simulating if 'results' was used instead of 'report'
                                   top_5_intents=self.top_5_intents,
                                   sentiment_trend_chart_data=self.sentiment_trend_chart_data,
                                   top_20_keywords_data=self.top_20_keywords_data,
                                   entity_overview_score=self.entity_overview_score,
                                   # Mocking flask_login's current_user
                                   current_user=MockUser(id=1, username="testuser"))

        with self.assertRaisesRegex(TemplateSyntaxError, "expected token '\\)', got 'x'"):
            self.client.get('/test_dashboard_render_fail')
            
    def test_render_results_dashboard_fixed_syntax_succeeds(self):
        # This test will be used after the template is fixed.
        # It assumes the fix involves using report.news_items and a 'to_dict' method.
        
        # Temporarily override the template content for this specific test case
        # to simulate the fixed version without modifying the file yet,
        # or, modify the file and then run this.
        # For now, let's assume the file will be fixed.

        # Define a route that uses the template
        @app.route('/test_dashboard_render_fixed')
        def test_dashboard_render_fixed():
            # This will render the actual 'results_dashboard.html' file.
            # Ensure the file is fixed before running this part of the test.
            return render_template('results_dashboard.html',
                                   report=self.report,
                                   # results=self.report.news_items, # If the template expects 'results' as news_items
                                   top_5_intents=self.top_5_intents,
                                   sentiment_trend_chart_data=self.sentiment_trend_chart_data,
                                   top_20_keywords_data=self.top_20_keywords_data,
                                   entity_overview_score=self.entity_overview_score,
                                   current_user=MockUser(id=1, username="testuser"))
        
        # If the template is fixed, this should not raise an error.
        # For now, this test is a placeholder for after the fix.
        # To make it runnable now, we'd need to mock render_template_string with fixed content.
        # Instead, we'll rely on fixing the file and then this test (or a similar one) passing.
        pass


if __name__ == '__main__':
    unittest.main()
