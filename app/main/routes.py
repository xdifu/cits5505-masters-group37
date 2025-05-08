# filepath: /home/god/cits5505-masters-group37/app/main/routes.py
# Defines the main routes for the application (index, analyze, results).

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Result, User
from app.forms import AnalysisForm, ShareForm, ManageSharingForm
from app.openai_api import analyze_sentiment
from collections import Counter # For counting sentiments
import sqlalchemy as sa
from datetime import datetime

# Create Blueprint for main application routes
bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """Displays the introductory/home page."""
    return render_template('index.html', title='Welcome')

@bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """Handles text submission for sentiment analysis."""
    form = AnalysisForm()
    sentiment_result_display = None # For non-AJAX display

    if form.validate_on_submit():
        news_text = form.news_text.data
        sentiment = analyze_sentiment(news_text)

        if sentiment and "Error:" not in sentiment:
            # Save result to database, associating with the current user
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
@login_required
def results():
    """Displays the user's past analysis results and a chart."""
    # Query results authored by the current user
    user_results = db.session.scalars(
        db.select(Result).where(Result.author == current_user).order_by(Result.timestamp.desc())
    ).all()

    # Calculate sentiment counts for the chart
    sentiment_counts = Counter(result.sentiment for result in user_results)
    chart_data = {
        'positive': sentiment_counts.get('Positive', 0),
        'neutral': sentiment_counts.get('Neutral', 0),
        'negative': sentiment_counts.get('Negative', 0)
    }

    return render_template('results.html', title='My Results',
                           results=user_results,
                           sentiment_counts=chart_data)

@bp.route('/shared_with_me')
@login_required
def shared_with_me():
    """Displays results shared with the current user by other users."""
    # Query results shared with the current user using the many-to-many relationship
    shared_results = db.session.scalars(current_user.results_shared_with_me.select().order_by(Result.timestamp.desc())).all()
    
    # Prepare data structure for template
    shared_items = []
    for result in shared_results:
        shared_items.append({
            'result_data': result,
            'shared_by': result.author,
            'shared_on': result.timestamp  # Using result timestamp as share timestamp
        })
    
    return render_template('shared_with_me.html', title='Shared With Me', shared_items=shared_items)

@bp.route('/result/<int:result_id>/manage_sharing', methods=['GET', 'POST'])
@login_required
def manage_sharing(result_id):
    """Manages the sharing settings for a specific analysis result."""
    result = db.session.get(Result, result_id)
    if not result or result.author != current_user:
        flash('Result not found or you are not authorized to manage its sharing.', 'danger')
        return redirect(url_for('main.results'))

    form = ManageSharingForm(current_user_id=current_user.id)

    if form.validate_on_submit():
        # Get currently shared users for this result
        currently_shared_with_ids = {user.id for user in result.shared_with_recipients}
        selected_user_ids = set(form.users_to_share_with.data)

        # Users to add (selected but not currently shared)
        users_to_add_ids = selected_user_ids - currently_shared_with_ids
        for user_id_to_add in users_to_add_ids:
            user_to_add = db.session.get(User, user_id_to_add)
            if user_to_add:
                result.shared_with_recipients.add(user_to_add)
        
        # Users to remove (currently shared but not selected)
        users_to_remove_ids = currently_shared_with_ids - selected_user_ids
        for user_id_to_remove in users_to_remove_ids:
            user_to_remove = db.session.get(User, user_id_to_remove)
            if user_to_remove:
                result.shared_with_recipients.remove(user_to_remove)
        
        db.session.commit()
        flash('Sharing settings updated successfully.', 'success')
        return redirect(url_for('main.manage_sharing', result_id=result.id))

    # Pre-populate the form with currently shared users for GET request
    form.users_to_share_with.data = [user.id for user in result.shared_with_recipients]
    
    all_other_users = db.session.scalars(sa.select(User).where(User.id != current_user.id).order_by(User.username)).all()
    return render_template('manage_sharing.html', title='Manage Sharing', 
                           form=form, result=result, all_other_users=all_other_users)

# Route to share a specific analysis result with a user
@bp.route('/results/<int:result_id>/share', methods=['GET', 'POST'])
@login_required
def share_analysis(result_id):
    """Shares a specific analysis result with another user."""
    result_to_share = db.session.get(Result, result_id)
    
    if not result_to_share:
        flash('Result not found.', 'danger')
        return redirect(url_for('main.results'))

    # Ensure the current user is the author of the result
    if result_to_share.author != current_user:
        flash('You can only share your own analysis results.', 'danger')
        return redirect(url_for('main.results'))

    form = ShareForm()
    if form.validate_on_submit():
        username_to_share_with = form.share_with_username.data
        user_to_share_with = db.session.scalar(sa.select(User).where(User.username == username_to_share_with))

        if not user_to_share_with:
            flash(f'User "{username_to_share_with}" not found.', 'warning')
        elif user_to_share_with == current_user:
            flash('You cannot share an analysis with yourself.', 'info')
        else:
            # Check if already shared with this user
            # For WriteOnlyCollection, query using with_parent
            # Use the actual class attribute for the relationship
            already_shared_query = db.session.query(User).with_parent(result_to_share, Result.shared_with_recipients).filter(User.id == user_to_share_with.id)
            is_already_shared = db.session.query(already_shared_query.exists()).scalar()

            if is_already_shared:
                flash(f'This result is already shared with {user_to_share_with.username}.', 'info')
            else:
                try:
                    # Add the user to the recipients list
                    result_to_share.shared_with_recipients.add(user_to_share_with)
                    db.session.commit()
                    flash(f'Analysis result shared successfully with {user_to_share_with.username}!', 'success')
                    return redirect(url_for('main.results'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error sharing result: {str(e)}', 'danger')
    
    return render_template('share_analysis.html', title='Share Analysis', form=form, result=result_to_share)