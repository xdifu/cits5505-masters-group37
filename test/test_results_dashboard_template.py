import pytest
from app import create_app

@pytest.fixture
def app():
    """
    Create and configure a new app instance for each test.
    """
    app = create_app()
    app.config['TESTING'] = True
    return app


def test_results_dashboard_template_compiles_and_renders(app):
    """
    Test that the results_dashboard.html template compiles without syntax errors
    and renders properly given minimal context.
    """
    with app.app_context():
        # Attempt to load and compile the template
        template = app.jinja_env.get_template('results_dashboard.html')
        assert template is not None, "Template failed to load."

        # Create a dummy result object with to_dict method
        class DummyResult:
            def to_dict(self):
                return {'id': 1, 'title': 'Test Title', 'value': 42}

        # Render with a list of DummyResult instances
        rendered = template.render(results=[DummyResult()], report_id=1)
        assert 'Test Title' in rendered, "Rendered output missing expected content."


def test_results_dashboard_template_empty_results(app):
    """
    Test rendering when results list is empty.
    """
    with app.app_context():
        template = app.jinja_env.get_template('results_dashboard.html')
        rendered = template.render(results=[], report_id=999)
        # Should not raise any exceptions and produce some base content
        assert 'Analysis Result' in rendered or 'My Results' in rendered
