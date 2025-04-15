# Defines the routes and view functions for the Flask application.

from flask import render_template, request, current_app as app
from .openai_api import analyze_sentiment

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handles requests to the main page.

    GET: Displays the form for submitting news text.
    POST: Receives text, analyzes sentiment via OpenAI API, and displays the result.

    Returns:
        Rendered HTML template with optional sentiment result.
    """
    sentiment_result = None # Initialize result variable

    # Handle form submission
    if request.method == 'POST':
        # Get the news text submitted by the user from the form
        news_text = request.form.get('news_text')

        # Check if text was actually provided
        if news_text:
            # Call the sentiment analysis function from the openai_api module
            sentiment_result = analyze_sentiment(news_text)
        else:
            # Handle case where the form was submitted empty
            sentiment_result = "Please enter some text to analyze."

    # Render the main page template.
    # Pass the sentiment result (if any) to the template.
    return render_template('index.html', sentiment=sentiment_result)