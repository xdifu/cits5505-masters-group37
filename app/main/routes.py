# filepath: c:\Users\Xiao Difu\Desktop\group5505\cits5505-masters-group37\app\main\routes.py
# Defines the main routes for the application (index, analyze, results dashboards, etc.).

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app # Removed Blueprint
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import AnalysisReport, NewsItem, User, analysis_report_shares # Updated import
from app.forms import AnalysisForm, ShareReportForm, ManageReportSharingForm # Updated import
from app.openai_api import analyze_text_data, SingleNewsItemAnalysis, PREDEFINED_INTENT_TAGS # Added PREDEFINED_INTENT_TAGS
from sqlalchemy.orm import aliased
from sqlalchemy import desc, or_
from typing import List, Optional, Dict, Any # Added List, Optional
import sqlalchemy as sa # Added sqlalchemy as sa
import json
from datetime import datetime, timedelta, timezone # Added timezone
import re # Added re
from collections import Counter, defaultdict # Added Counter, defaultdict

# Helper function to parse string dates from OpenAI into datetime objects
def _parse_publication_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str: 
        return None
    try:
        # Attempt to parse YYYY-MM-DD format
        return datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except ValueError:
        # Add more formats or more robust parsing if needed
        print(f"Warning: Could not parse date string: {date_str}")
        return None

# Helper function to prepare aggregated data for an AnalysisReport
def _prepare_report_aggregates(news_items: List[NewsItem]) -> Dict[str, Any]:
    """
    Processes a list of NewsItem objects to generate aggregated data for dashboard components.
    Returns a dictionary with keys for aggregated_intents_json, aggregated_keywords_json,
    sentiment_trend_json, overall_sentiment_label, and overall_sentiment_score.
    """
    if not news_items:
        return {
            'aggregated_intents_json': json.dumps({}),
            'aggregated_keywords_json': json.dumps([]),
            'sentiment_trend_json': json.dumps({'dates': [], 'overall_scores': [], 'keyword_trends': {}}),
            'overall_sentiment_label': 'Neutral',
            'overall_sentiment_score': 0.0
        }

    all_intents_flat = []
    all_keywords_with_sentiment = [] # List of tuples (keyword, sentiment_score)
    all_sentiment_scores = []
    daily_sentiment_scores = defaultdict(lambda: {'scores': [], 'keywords': defaultdict(lambda: {'scores': []}) })
    all_item_keywords = [] # Corrected initialization

    for item in news_items:
        all_sentiment_scores.append(item.sentiment_score)
        item_intents = item.get_intents() # Uses helper from NewsItem model
        all_intents_flat.extend(item_intents)
        
        item_keywords = item.get_keywords()
        all_item_keywords.extend(item_keywords)
        for kw in item_keywords:
            all_keywords_with_sentiment.append((kw, item.sentiment_score))

        if item.publication_date:
            date_str = item.publication_date.strftime('%Y-%m-%d')
            daily_sentiment_scores[date_str]['scores'].append(item.sentiment_score)
            for kw in item_keywords:
                 daily_sentiment_scores[date_str]['keywords'][kw]['scores'].append(item.sentiment_score)

    # 1. Aggregated Intents (Top 5)
    intent_counts = Counter(all_intents_flat)
    top_5_intents = dict(intent_counts.most_common(5))
    # Calculate percentages for pie chart
    total_intents_counted = sum(top_5_intents.values())
    intents_share_data = {intent: (count / total_intents_counted * 100) if total_intents_counted > 0 else 0 
                          for intent, count in top_5_intents.items()}

    # 2. Aggregated Keywords (Top 20 with average sentiment)
    keyword_occurrences = Counter(kw for kw, score in all_keywords_with_sentiment)
    aggregated_keywords_data = []
    for kw, count in keyword_occurrences.most_common(20):
        kw_scores = [score for k, score in all_keywords_with_sentiment if k == kw]
        avg_sentiment = sum(kw_scores) / len(kw_scores) if kw_scores else 0
        aggregated_keywords_data.append({'text': kw, 'count': count, 'avg_sentiment': round(avg_sentiment, 2)})

    # 3. Sentiment Trend Over Time
    sorted_dates = sorted(daily_sentiment_scores.keys())
    overall_trend_scores = []
    for date_str in sorted_dates:
        avg_score = sum(daily_sentiment_scores[date_str]['scores']) / len(daily_sentiment_scores[date_str]['scores']) \
            if daily_sentiment_scores[date_str]['scores'] else 0
        overall_trend_scores.append(round(avg_score, 2))
    
    # Top 3 keywords for trend lines
    top_3_overall_keywords = [kw for kw, count in Counter(all_item_keywords).most_common(3)]
    keyword_trends_data = {}
    for kw in top_3_overall_keywords:
        keyword_daily_scores = []
        for date_str in sorted_dates:
            kw_day_scores = daily_sentiment_scores[date_str]['keywords'][kw]['scores']
            avg_kw_day_score = sum(kw_day_scores) / len(kw_day_scores) if kw_day_scores else 0 # Or carry forward previous if no data?
            keyword_daily_scores.append(round(avg_kw_day_score,2))
        keyword_trends_data[kw] = keyword_daily_scores
        
    sentiment_trend_data = {
        'dates': sorted_dates,
        'overall_scores': overall_trend_scores,
        'keyword_trends': keyword_trends_data # { 'keyword1': [scores], 'keyword2': [scores] }
    }

    # 4. Overall Sentiment Score and Label for the report
    overall_avg_score = sum(all_sentiment_scores) / len(all_sentiment_scores) if all_sentiment_scores else 0.0
    overall_sentiment_label = "Neutral"
    if overall_avg_score > 0.2:
        overall_sentiment_label = "Positive"
    elif overall_avg_score < -0.2:
        overall_sentiment_label = "Negative"

    return {
        'aggregated_intents_json': json.dumps(intents_share_data),
        'aggregated_keywords_json': json.dumps(aggregated_keywords_data),
        'sentiment_trend_json': json.dumps(sentiment_trend_data),
        'overall_sentiment_label': overall_sentiment_label,
        'overall_sentiment_score': round(overall_avg_score, 2)
    }

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Welcome')

@bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    form = AnalysisForm()
    if form.validate_on_submit():
        # Corrected f-string for report_name default value by removing the erroneous newline character within it
        report_name = form.report_name.data or f"Analysis on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
        raw_news_text = form.news_text.data
        
        # Split text into items: by one or more empty lines
        news_text_items = [item.strip() for item in re.split(r'\n\s*\n', raw_news_text) if item.strip()]
        if not news_text_items:
            # If re.split doesn't work (e.g. single block of text), treat as one item
            if raw_news_text.strip():
                 news_text_items = [raw_news_text.strip()]
            else:
                flash('No text provided for analysis.', 'warning')
                return render_template('analyze.html', title='Analyze Text', form=form)

        new_analysis_report = AnalysisReport(
            name=report_name,
            author=current_user,
            # Placeholder values, will be updated after processing items
            overall_sentiment_label='Processing...',
            overall_sentiment_score=0.0,
            aggregated_intents_json=json.dumps({}),
            aggregated_keywords_json=json.dumps([]),
            sentiment_trend_json=json.dumps({})
        )
        db.session.add(new_analysis_report)
        # We need the report ID for news items, so flush to get it.
        db.session.flush() 

        created_news_items = []
        for text_item in news_text_items:
            if not text_item:
                continue
            # Call the new function to get sentiment, intents, and keywords
            analysis_result: SingleNewsItemAnalysis = analyze_text_data(text_item)
            
            pub_date = _parse_publication_date(analysis_result.publication_date)

            news_item_db = NewsItem(
                original_text=text_item,
                sentiment_label=analysis_result.sentiment_label.value,
                sentiment_score=analysis_result.sentiment_score,
                analysis_report_id=new_analysis_report.id, # Link to parent report
                publication_date=pub_date
            )
            news_item_db.set_intents(analysis_result.intents or [])
            news_item_db.set_keywords(analysis_result.keywords or [])
            db.session.add(news_item_db)
            created_news_items.append(news_item_db)
        
        if not created_news_items:
            db.session.rollback() # Rollback report creation if no items were processed
            flash('Could not process any news items from the provided text.', 'danger')
            return render_template('analyze.html', title='Analyze Text', form=form)

        # Now that all news items are created (but not yet committed), calculate aggregates
        db.session.flush() # Ensure news_items have IDs and are associated
        
        aggregates = _prepare_report_aggregates(created_news_items)
        new_analysis_report.overall_sentiment_label = aggregates['overall_sentiment_label']
        new_analysis_report.overall_sentiment_score = aggregates['overall_sentiment_score']
        new_analysis_report.aggregated_intents_json = aggregates['aggregated_intents_json']
        new_analysis_report.aggregated_keywords_json = aggregates['aggregated_keywords_json']
        new_analysis_report.sentiment_trend_json = aggregates['sentiment_trend_json']
        
        db.session.commit()
        flash(f'Report "{new_analysis_report.name}" created successfully with {len(created_news_items)} item(s)!', 'success')
        return redirect(url_for('main.results_dashboard', report_id=new_analysis_report.id))

    return render_template('analyze.html', title='New Analysis Report', form=form)


@bp.route('/results')
@login_required
def results():
    """Displays a list of the user's analysis reports."""
    user_reports = db.session.scalars(
        db.select(AnalysisReport).where(AnalysisReport.author == current_user).order_by(AnalysisReport.timestamp.desc())
    ).all()
    return render_template('results.html', title='My Analysis Reports', reports=user_reports)


@bp.route('/results_dashboard/<int:report_id>')
@login_required
def results_dashboard(report_id):
    report = db.session.get(AnalysisReport, report_id)
    if report is None:
        flash('Analysis report not found.')
        return redirect(url_for('main.index'))

    # Check if the current user is the author or if the report has been shared with them
    # Corrected the filter to use analysis_report_shares.c.recipient_id
    # and also filter by analysis_report_id
    shared_report_entry = db.session.query(analysis_report_shares).filter(
        analysis_report_shares.c.analysis_report_id == report_id,
        analysis_report_shares.c.recipient_id == current_user.id
    ).first()

    # Corrected to use report.author.id instead of report.author_id
    if report.author.id != current_user.id and shared_report_entry is None:
        flash('You do not have permission to view this report.')
        return redirect(url_for('main.index'))

    # Convert NewsItem objects to dictionaries for JSON serialization
    # Changed to use db.select() and db.session.scalars() because news_items is WriteOnlyMapped
    news_items_data = [item.to_dict() for item in 
                      db.session.scalars(db.select(NewsItem).where(NewsItem.analysis_report_id == report.id)).all()]

    return render_template(
        'results_dashboard.html',
        title=f"Dashboard for {report.name}",
        report=report,
        news_items=news_items_data,  # Pass serialized news items
        all_intents_list=PREDEFINED_INTENT_TAGS,
        current_app_config=current_app.config # Pass current_app.config
    )

# API endpoint for fetching filtered data for the dashboard
@bp.route('/api/filtered_report_data/<int:report_id>', methods=['POST'])
@login_required
def api_filtered_report_data(report_id):
    report = db.session.get(AnalysisReport, report_id)
    if report is None:
        return jsonify({'error': 'Report not found'}), 404

    # Permission check (author or shared with)
    # Corrected the filter to use analysis_report_shares.c.recipient_id
    # and also filter by analysis_report_id
    shared_report_entry = db.session.query(analysis_report_shares).filter(
        analysis_report_shares.c.analysis_report_id == report_id,
        analysis_report_shares.c.recipient_id == current_user.id
    ).first()
    # Corrected to use report.author.id instead of report.author_id
    if report.author.id != current_user.id and shared_report_entry is None:
        return jsonify({'error': 'Unauthorized to access this report'}), 403

    filters = request.json
    if not filters:
        return jsonify({'error': 'No filters provided'}), 400

    query = NewsItem.query.filter_by(report_id=report_id)

    # Date Range Filter
    date_range = filters.get('date_range')
    if date_range and date_range.get('start') and date_range.get('end'):
        try:
            start_date_str = date_range['start']
            end_date_str = date_range['end']
            # Assuming YYYY-MM-DD format from flatpickr
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            # Add one day to end_date to make the range inclusive for the end day
            end_date = (datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)).replace(tzinfo=timezone.utc)
            query = query.filter(NewsItem.publication_date >= start_date, NewsItem.publication_date < end_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400
            
    # Sentiment Score Range Filter
    min_sentiment = filters.get('min_sentiment')
    max_sentiment = filters.get('max_sentiment')
    if min_sentiment is not None:
        query = query.filter(NewsItem.sentiment_score >= float(min_sentiment))
    if max_sentiment is not None:
        query = query.filter(NewsItem.sentiment_score <= float(max_sentiment))

    # Intent Tags Filter (multi-select, OR logic for selected intents)
    intent_tags = filters.get('intent_tags')
    if intent_tags and isinstance(intent_tags, list) and len(intent_tags) > 0:
        # Assuming intents are stored as a JSON list in the NewsItem model, e.g., '["Inform", "Opinion"]'
        # This requires a more complex query depending on how intents are stored (e.g., JSONB contains, like)
        # For simple JSON list of strings:
        intent_conditions = []
        for tag in intent_tags:
            # Use sa.func.json_contains(NewsItem.intents_json, sa.cast(f'"{tag}"', sa.JSON)) for PostgreSQL/MySQL
            # For SQLite, json_each can be used or a simple LIKE for stringified JSON.
            # Using LIKE as a fallback, assuming intents_json is a string like '["tag1", "tag2"]'
            intent_conditions.append(NewsItem.intents_json.like(f'%"{tag}"%'))
        if intent_conditions:
            query = query.filter(or_(*intent_conditions))
            
    # Keywords Filter (comma-separated, AND logic for keywords)
    keywords_str = filters.get('keywords')
    if keywords_str:
        keywords_list = [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()]
        if keywords_list:
            # Similar to intents, this depends on how keywords are stored.
            # Using LIKE as a fallback, assuming keywords_json is a string like '[{"text": "kw1", "sentiment": 0.5}, ...]'
            # or a simpler '["kw1", "kw2"]'
            for kw in keywords_list:
                query = query.filter(NewsItem.keywords_json.like(f'%"{kw}"%')) # Adjust based on actual JSON structure

    filtered_news_items_models = query.order_by(desc(NewsItem.publication_date)).all()
    
    # Re-calculate aggregates based on filtered items
    if not filtered_news_items_models:
        # Return empty/default aggregates if no items match filters
        empty_aggregates = {
            "aggregated_intents_json": json.dumps({"labels": [], "datasets": [{"data": [], "backgroundColor": ["#CCCCCC"], "label": "No data"}]}),
            "aggregated_keywords_json": json.dumps([]),
            "sentiment_trend_json": json.dumps({"labels": [], "datasets": [{"label": "Overall Sentiment", "data": [], "borderColor": "#CCCCCC", "fill": False}]}),
            "overall_sentiment_score": 0,
            "overall_sentiment_label": "Neutral"
        }
        response_data = {
            "report_aggregates": empty_aggregates,
            "news_items": []
        }
    else:
        aggregates = _prepare_report_aggregates(filtered_news_items_models) # This function needs to handle NewsItem instances
        response_data = {
            "report_aggregates": aggregates, # _prepare_report_aggregates should return a dict with JSON strings
            "news_items": [item.to_dict() for item in filtered_news_items_models]
        }

    return jsonify(response_data)


# --- Sharing Routes (Updated for AnalysisReport) ---
@bp.route('/share_report/<int:report_id>', methods=['GET', 'POST'])
@login_required
def share_report(report_id):
    report = db.session.get(AnalysisReport, report_id)
    # Corrected to use report.author.id
    if not report or report.author.id != current_user.id:
        flash('Analysis report not found or you do not own this report.', 'danger')
        return redirect(url_for('main.results'))

    form = ShareReportForm()
    if form.validate_on_submit():
        user_to_share_with = db.session.scalar(
            db.select(User).where(User.username == form.share_with_username.data)
        )
        if user_to_share_with is None:
            flash(f'User {form.share_with_username.data} not found.', 'danger')
        elif user_to_share_with == current_user:
            flash('You cannot share a report with yourself.', 'warning')
        elif db.session.scalar(report.shared_with_recipients.select().where(User.id == user_to_share_with.id)):
            flash(f'Report already shared with {user_to_share_with.username}.', 'info')
        else:
            report.shared_with_recipients.append(user_to_share_with)
            db.session.commit()
            flash(f'Report shared successfully with {user_to_share_with.username}.', 'success')
        return redirect(url_for('main.results_dashboard', report_id=report_id))
    
    return render_template('share_analysis.html', title='Share Report', form=form, report=report)

@bp.route('/manage_report_sharing/<int:report_id>', methods=['GET', 'POST'])
@login_required
def manage_report_sharing(report_id):
    report = db.session.get(AnalysisReport, report_id)
    # Corrected to use report.author.id
    if not report or report.author.id != current_user.id:
        flash('Analysis report not found or you do not own this report.', 'danger')
        return redirect(url_for('main.results'))

    form = ManageReportSharingForm()
    potential_recipients = db.session.scalars(db.select(User).where(User.id != current_user.id)).all()
    form.users_to_share_with.choices = [(u.id, u.username) for u in potential_recipients]

    if form.validate_on_submit():
        current_shared_ids = {user.id for user in report.shared_with_recipients}
        selected_ids = set(form.users_to_share_with.data)

        ids_to_add = selected_ids - current_shared_ids
        for user_id_to_add in ids_to_add:
            user = db.session.get(User, user_id_to_add)
            if user: report.shared_with_recipients.append(user)
        
        ids_to_remove = current_shared_ids - selected_ids
        for user_id_to_remove in ids_to_remove:
            user = db.session.get(User, user_id_to_remove)
            if user: report.shared_with_recipients.remove(user)
            
        db.session.commit()
        flash('Sharing settings updated.', 'success')
        return redirect(url_for('main.results_dashboard', report_id=report_id))

    form.users_to_share_with.data = [user.id for user in report.shared_with_recipients]
    return render_template('manage_sharing.html', title='Manage Sharing', form=form, report=report)


@bp.route('/shared_with_me')
@login_required
def shared_with_me():
    reports = db.session.scalars(
        current_user.analysis_reports_shared_with_me.select().order_by(AnalysisReport.timestamp.desc())
    ).all()
    return render_template('shared_with_me.html', title='Shared With Me', reports=reports)


@bp.route('/shared_report_details/<int:report_id>')
@login_required
def shared_report_details(report_id):
    report = db.session.get(AnalysisReport, report_id)
    is_owner = (report and report.user_id == current_user.id)
    is_shared_with_current_user = db.session.scalar(report.shared_with_recipients.select().where(User.id == current_user.id)) if report else False

    if not report or not (is_owner or is_shared_with_current_user):
        flash('Analysis report not found or access denied.', 'danger')
        return redirect(url_for('main.shared_with_me'))

    # Updated to use db.select() and db.session.scalars() because news_items is WriteOnlyMapped
    news_items_for_feed = db.session.scalars(
        db.select(NewsItem)
        .where(NewsItem.analysis_report_id == report_id)
        .order_by(NewsItem.publication_date.desc().nulls_last(), NewsItem.id.desc())
    ).all()

    return render_template('results_dashboard.html',
                           title=f'Dashboard: {report.name} (Shared by {report.author.username})',
                           report=report,
                           news_items=news_items_for_feed,
                           all_intents_list=PREDEFINED_INTENT_TAGS,
                           is_shared_view=True
                           )

# Old /results route (from before AnalysisReport) is now /results_list
# Old /share_analysis and /manage_sharing are updated to /share_report and /manage_report_sharing
# Old /shared_results/<id> is now /shared_report_details/<id>