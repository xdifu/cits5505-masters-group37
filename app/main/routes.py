# filepath: /home/god/web-group-project/cits5505-masters-group37/news-sentiment-analyzer/app/main/routes.py
# Defines the main routes for the application (index, analyze, results).

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Result, User
# Assuming AnalysisForm is needed for CSRF in toggle_share or potentially analyze page enhancements
from app.forms import AnalysisForm
from app.openai_api import analyze_sentiment
from collections import Counter # For counting sentiments

# Create Blueprint for main application routes
bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """Displays the introductory/home page."""
    # Renders the welcome page
    return render_template('index.html', title='Welcome')

@bp.route('/analyze', methods=['GET', 'POST'])
# @login_required # Temporarily commented out for static GUI demo
def analyze():
    """Handles text submission for sentiment analysis."""
    form = AnalysisForm()
    sentiment_result_display = None # For non-AJAX display

    if form.validate_on_submit():
        news_text = form.news_text.data
        sentiment = analyze_sentiment(news_text)

        if sentiment and "Error:" not in sentiment:
            # Save result to database
            result = Result(original_text=news_text, sentiment=sentiment, author=current_user)
            db.session.add(result)
            db.session.commit()
            flash('Analysis complete and saved!', 'success')
            sentiment_result_display = sentiment # For display on page reload

            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'sentiment': sentiment, 'message': 'Analysis complete and saved!'})

            # For non-AJAX, clear form and stay on page showing result
            form.news_text.data = ''
        else:
            flash(f'Analysis failed: {sentiment}', 'danger')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': sentiment or 'Analysis failed'}), 400

    # For GET request or failed validation
    return render_template('analyze.html', title='Analyze Text', form=form, sentiment_result=sentiment_result_display)


@bp.route('/results')
# @login_required # Temporarily commented out for static GUI demo
def results():
    """Displays the user's past analysis results and a chart."""
    # Use scalars() for potentially large result sets and .all() to get the list
    user_results = db.session.scalars(
        db.select(Result).where(Result.user_id == current_user.id).order_by(Result.timestamp.desc())
    ).all()

    # Calculate sentiment counts for the chart
    sentiment_counts = Counter(result.sentiment for result in user_results)
    chart_data = {
        'positive': sentiment_counts.get('Positive', 0),
        'neutral': sentiment_counts.get('Neutral', 0),
        'negative': sentiment_counts.get('Negative', 0)
    }

    # Pass a form instance for CSRF token in toggle action
    share_form = AnalysisForm() # Re-use form for CSRF token

    return render_template('results.html', title='My Results',
                           results=user_results,
                           sentiment_counts=chart_data,
                           share_form=share_form) # Pass form for CSRF

@bp.route('/results/toggle_share/<int:result_id>', methods=['POST'])
@login_required
def toggle_share(result_id):
    """Toggles the shared status of a specific result."""
    result = db.session.get(Result, result_id)
    if result is None:
        flash('Result not found.', 'danger')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Result not found'}), 404
        return redirect(url_for('main.results'))

    if result.author != current_user:
        flash('You do not have permission to modify this result.', 'danger')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Permission denied'}), 403
        return redirect(url_for('main.results'))

    # Toggle the shared status
    result.shared = not result.shared
    db.session.commit()
    message = 'Result shared publicly.' if result.shared else 'Result made private.'
    flash(message, 'success')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'shared': result.shared, 'message': message})

    return redirect(url_for('main.results'))


@bp.route('/shared')
# @login_required # Temporarily commented out for static GUI demo
def shared_results():
    """Displays results shared by all users."""
    shared = db.session.scalars(
        db.select(Result).where(Result.shared == True).order_by(Result.timestamp.desc())
    ).all()
    # Ensure author relationship is loaded efficiently if needed often
    # Consider adding options=so.selectinload(Result.author) to the select statement
    return render_template('shared_results.html', title='Shared Results', shared_results=shared)

# Add other routes like delete_result if needed