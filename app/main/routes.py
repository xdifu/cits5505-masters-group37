# filepath: c:\Users\Xiao Difu\Desktop\group5505\cits5505-masters-group37\app\main\routes.py
# Defines the main routes for the application (index, analyze, results dashboards, etc.).

from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import AnalysisReport, NewsItem, analysis_report_shares, User
from app.forms import AnalysisForm, ShareReportForm, ManageSharingForm # Fixed class name
from app.openai_api import analyze_text_data, SingleNewsItemAnalysis, PREDEFINED_INTENT_TAGS, SentimentEnum # Added SentimentEnum here
from sqlalchemy.orm import aliased
from sqlalchemy import desc, or_, select, func # Ensure select is imported
from typing import List, Optional, Dict, Any # Added List, Optional
import json # Added json
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
            'overall_sentiment_label': "Neutral",
            'overall_sentiment_score': 0.0
        }

    all_intents_flat = []
    all_keywords_with_sentiment = [] # List of tuples (keyword, sentiment_score)
    all_sentiment_scores = []
    # Using defaultdict for easier aggregation
    daily_sentiment_scores = defaultdict(lambda: {'scores': [], 'keywords': defaultdict(lambda: {'scores': []}) })
    all_item_keywords = []

    for item in news_items:
        if item.intents:
            try:
                # Intents are stored as a JSON string list in the NewsItem model
                item_intents = json.loads(item.intents)
                if isinstance(item_intents, list):
                    all_intents_flat.extend(item_intents)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse intents_json for NewsItem ID {item.id}: {item.intents}")
        
        if item.keywords:
            try:
                # Keywords are stored as a JSON string list in the NewsItem model
                item_keywords_list = json.loads(item.keywords)
                if isinstance(item_keywords_list, list):
                    all_item_keywords.extend(item_keywords_list) # For overall keyword frequency
                    for kw in item_keywords_list:
                        # Associate keyword with the item's overall sentiment score
                        all_keywords_with_sentiment.append((kw, item.sentiment_score or 0.0))
            except json.JSONDecodeError:
                print(f"Warning: Could not parse keywords_json for NewsItem ID {item.id}: {item.keywords}")

        if item.sentiment_score is not None:
            all_sentiment_scores.append(item.sentiment_score)
        
        if item.publication_date and item.sentiment_score is not None:
            # Ensure publication_date is a datetime object
            pub_date = item.publication_date
            if isinstance(pub_date, str): # Should ideally be datetime object from DB
                pub_date = _parse_publication_date(pub_date)

            if pub_date:
                date_str = pub_date.strftime('%Y-%m-%d')
                daily_sentiment_scores[date_str]['scores'].append(item.sentiment_score)
                if item.keywords: # Check again for safety
                    try:
                        item_keywords_list_for_trend = json.loads(item.keywords)
                        if isinstance(item_keywords_list_for_trend, list):
                            for kw in item_keywords_list_for_trend:
                                daily_sentiment_scores[date_str]['keywords'][kw]['scores'].append(item.sentiment_score)
                    except json.JSONDecodeError:
                        pass # Already warned above

    # 1. Aggregated Intents (Top 5)
    intent_counts = Counter(all_intents_flat)
    top_5_intents = dict(intent_counts.most_common(5))
    total_intents_counted = sum(top_5_intents.values())
    intents_share_data = {intent: (count / total_intents_counted * 100) if total_intents_counted > 0 else 0 
                          for intent, count in top_5_intents.items()}

    # 2. Aggregated Keywords (Top 20 with average sentiment)
    keyword_occurrences = Counter(kw for kw, score in all_keywords_with_sentiment)
    aggregated_keywords_data = []
    for kw, count in keyword_occurrences.most_common(20):
        # Calculate average sentiment for this keyword
        kw_sentiment_scores = [score for k, score in all_keywords_with_sentiment if k == kw]
        avg_sentiment = sum(kw_sentiment_scores) / len(kw_sentiment_scores) if kw_sentiment_scores else 0.0
        # Determine color based on average sentiment
        color = "grey" # Neutral
        if avg_sentiment > 0.2:
            color = "green" # Positive
        elif avg_sentiment < -0.2:
            color = "red" # Negative
        aggregated_keywords_data.append({"text": kw, "value": count, "avg_sentiment": round(avg_sentiment, 2), "color": color})


    # 3. Sentiment Trend Over Time
    sorted_dates = sorted(daily_sentiment_scores.keys())
    overall_trend_scores = []
    for date_str in sorted_dates:
        avg_score_for_date = sum(daily_sentiment_scores[date_str]['scores']) / len(daily_sentiment_scores[date_str]['scores']) if daily_sentiment_scores[date_str]['scores'] else 0
        overall_trend_scores.append(round(avg_score_for_date, 2))
    
    top_3_overall_keywords = [kw for kw, count in Counter(all_item_keywords).most_common(3)]
    keyword_trends_data = {}
    for kw in top_3_overall_keywords:
        keyword_trend_line = []
        for date_str in sorted_dates:
            if daily_sentiment_scores[date_str]['keywords'][kw]['scores']:
                avg_kw_score_for_date = sum(daily_sentiment_scores[date_str]['keywords'][kw]['scores']) / len(daily_sentiment_scores[date_str]['keywords'][kw]['scores'])
                keyword_trend_line.append(round(avg_kw_score_for_date, 2))
            else:
                keyword_trend_line.append(None) # Or 0, or skip point, depending on chart handling
        keyword_trends_data[kw] = keyword_trend_line
        
    sentiment_trend_data = {
        'dates': sorted_dates,
        'overall_scores': overall_trend_scores,
        'keyword_trends': keyword_trends_data
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
        'aggregated_keywords_json': json.dumps(aggregated_keywords_data), # Now includes avg_sentiment and color
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
    analysis_data_for_template = None # Used for non-AJAX responses

    if form.validate_on_submit():
        text_data = form.news_text.data
        report_name = form.report_name.data or f"Analysis on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
        
        raw_texts = text_data.split('---NEXT_ITEM---')
        if not raw_texts or all(not t.strip() for t in raw_texts):
            if is_ajax_request():
                return jsonify({'error': 'No text provided for analysis.'}), 400
            flash('No text provided for analysis.', 'warning')
            return render_template('analyze.html', title='Analyze Text', form=form, analysis_data=analysis_data_for_template)

        try:
            new_report = AnalysisReport(
                name=report_name,
                author=current_user,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(new_report)
            db.session.flush()  # Get new_report.id for associations
            
            created_news_items_details = []
            overall_sentiments = []

            for single_text in raw_texts:
                if not single_text.strip():
                    continue
                
                analysis_result: SingleNewsItemAnalysis = analyze_text_data(single_text.strip())
                
                # Parse the publication date string from OpenAI into a datetime object
                parsed_publication_date = _parse_publication_date(analysis_result.publication_date)

                news_item = NewsItem(
                    original_text=single_text.strip(),
                    sentiment_label=analysis_result.sentiment_label,
                    sentiment_score=analysis_result.sentiment_score,
                    intents=json.dumps(analysis_result.intents),
                    keywords=json.dumps(analysis_result.keywords),
                    analysis_report_id=new_report.id,
                    publication_date=parsed_publication_date # Set the publication_date field
                    # timestamp=datetime.now(timezone.utc) # REMOVE: This was causing the error
                )
                db.session.add(news_item)
                
                created_news_items_details.append({
                    "original_text": single_text.strip(),
                    "sentiment": analysis_result.sentiment_label,
                    "sentiment_score": analysis_result.sentiment_score,
                    "intents": analysis_result.intents,
                    "keywords": analysis_result.keywords
                })
                if analysis_result.sentiment_score is not None:
                    overall_sentiments.append(analysis_result.sentiment_score)

            if not created_news_items_details:
                db.session.rollback() # Rollback report if no items processed
                if is_ajax_request():
                    return jsonify({'error': 'No valid text items found for analysis after splitting.'}), 400
                flash('No valid text items found for analysis after splitting.', 'warning')
                return render_template('analyze.html', title='Analyze Text', form=form, analysis_data=analysis_data_for_template)

            if overall_sentiments:
                new_report.overall_sentiment_score = sum(overall_sentiments) / len(overall_sentiments)
            
            db.session.commit()

            if is_ajax_request():
                # For AJAX, return JSON with details of the first item or a summary
                first_item_analysis = created_news_items_details[0] if created_news_items_details else {}
                return jsonify({
                    'message': f'Analysis report "{new_report.name}" created successfully! {len(created_news_items_details)} item(s) processed.',
                    'sentiment': first_item_analysis.get('sentiment'),
                    'sentiment_score': first_item_analysis.get('sentiment_score'),
                    'intents': first_item_analysis.get('intents'),
                    'keywords': first_item_analysis.get('keywords'),
                    'report_id': new_report.id,
                    'report_url': url_for('main.results_dashboard', report_id=new_report.id)
                })

            flash(f'Analysis report "{new_report.name}" created successfully!', 'success')
            return redirect(url_for('main.results_dashboard', report_id=new_report.id))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving analysis report: {e}", exc_info=True)
            if is_ajax_request():
                return jsonify({'error': f'An error occurred during analysis: {str(e)}'}), 500
            flash('Error saving analysis results. Please try again.', 'danger')
            # For non-AJAX, render the form again
            return render_template('analyze.html', title='Analyze Text', form=form, analysis_data=analysis_data_for_template)

    elif request.method == 'POST': # Catches POST requests where form.validate_on_submit() is False
        if is_ajax_request():
            # Form validation failed for an AJAX request, return errors as JSON
            return jsonify({'errors': form.errors}), 400 # 400 Bad Request
        else:
            # For non-AJAX POST with form errors, flash a general message.
            # WTForms will typically display specific field errors in the template.
            flash('Please correct the errors highlighted below.', 'warning')
            # Fall through to render the template with form errors displayed

    # Handles GET requests, and non-AJAX POSTs where form validation failed
    return render_template('analyze.html', title='Analyze Text', form=form, analysis_data=analysis_data_for_template)

#  replace request.is_xhr
def is_ajax_request():
    """Check if the request was made with AJAX."""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

@bp.route('/results')
@login_required
def results():
    # 1) load the current user's reports
    user_reports = db.session.scalars(
        select(AnalysisReport)
        .where(AnalysisReport.user_id == current_user.id)
        .order_by(AnalysisReport.timestamp.desc())
    ).all()

    # 2) compute how many NewsItems each report has
    counts = dict(
        db.session.query(
            NewsItem.analysis_report_id,
            func.count(NewsItem.id)
        )
        .filter(NewsItem.analysis_report_id.in_([r.id for r in user_reports]))
        .group_by(NewsItem.analysis_report_id)
        .all()
    )
    for rpt in user_reports:
        rpt.item_count = counts.get(rpt.id, 0)

    # 3) build your sentiment_counts as before...
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    user_news_items = db.session.scalars(
        select(NewsItem)
        .join(NewsItem.analysis_report)
        .where(AnalysisReport.user_id == current_user.id)
    ).all()
    for item in user_news_items:
        if item.sentiment_label == SentimentEnum.POSITIVE:
            sentiment_counts['positive'] += 1
        elif item.sentiment_label == SentimentEnum.NEUTRAL:
            sentiment_counts['neutral'] += 1
        elif item.sentiment_label == SentimentEnum.NEGATIVE:
            sentiment_counts['negative'] += 1

    return render_template(
        'results.html',
        title='My Analysis Results',
        results=user_reports,
        sentiment_counts=sentiment_counts
    )

@bp.route('/results_dashboard/<int:report_id>')
@login_required
def results_dashboard(report_id):
    report = db.session.get(AnalysisReport, report_id)

    if report is None:
        flash('Analysis report not found.', 'danger')
        return redirect(url_for('main.results')) # Redirect to the list of reports

    # Check permission: user must be the author or it must be shared with them
    is_author = report.user_id == current_user.id
    
    # Correctly check if the report is shared with the current user
    # by querying the association table directly.
    stmt = db.select(analysis_report_shares).where(
        (analysis_report_shares.c.analysis_report_id == report.id) &
        (analysis_report_shares.c.recipient_id == current_user.id)
    )
    # is_shared_with_current_user will be True if a record exists, False otherwise.
    is_shared_with_current_user = db.session.execute(db.select(stmt.exists())).scalar()

    if not is_author and not is_shared_with_current_user:
        flash('You do not have permission to view this report.', 'danger')
        return redirect(url_for('main.results'))

    # Fetch all news items associated with this report, explicitly ordered
    # news_items_for_feed = report.news_items.order_by(NewsItem.publication_date.desc().nullslast(), NewsItem.id.desc()).all()
    # ^^^ This line caused: AttributeError: 'WriteOnlyCollection' object has no attribute 'order_by'
    
    # Corrected approach: Build the query explicitly
    stmt = db.select(NewsItem).where(NewsItem.analysis_report_id == report.id).order_by(
        NewsItem.publication_date.desc().nullslast(), 
        NewsItem.id.desc()
    )
    news_items_for_feed = db.session.scalars(stmt).all()

    # The aggregated data is already stored in the report model, so we just load it.
    try:
        top_5_intents_data = json.loads(report.aggregated_intents_json) if report.aggregated_intents_json else {}
        sentiment_trend_data = json.loads(report.sentiment_trend_json) if report.sentiment_trend_json else {}
        top_20_keywords_data = json.loads(report.aggregated_keywords_json) if report.aggregated_keywords_json else []
    except json.JSONDecodeError:
        flash('Error decoding stored report data. Please try re-analyzing.', 'warning')
        # Provide default empty structures if JSON is corrupted
        top_5_intents_data = {}
        sentiment_trend_data = {'dates': [], 'overall_scores': [], 'keyword_trends': {}}
        top_20_keywords_data = []
    
    overall_sentiment_score_for_gauge = report.overall_sentiment_score if report.overall_sentiment_score is not None else 0.0

    # Prepare news_items_for_feed as a list of dicts
    news_items_for_feed_dicts = [item.to_dict() for item in news_items_for_feed]

    # Consolidate all data for JavaScript into a single dictionary
    flask_to_js_data = {
        'reportId': report.id,
        'top5IntentsData': top_5_intents_data,
        'sentimentTrendData': sentiment_trend_data,
        'top20KeywordsData': top_20_keywords_data,
        'entityOverviewScore': overall_sentiment_score_for_gauge,
        'initialNewsItems': news_items_for_feed_dicts
    }

    return render_template(
        'results_dashboard.html',
        title=f"Dashboard: {report.name}",
        report=report,
        # Pass the consolidated data object to the template
        flask_to_js_data_json=json.dumps(flask_to_js_data), 
        # Keep individual variables if they are used elsewhere in the template directly
        news_items_for_feed=news_items_for_feed_dicts, 
        top_5_intents=top_5_intents_data,
        sentiment_trend_chart_data=sentiment_trend_data,
        top_20_keywords_data=top_20_keywords_data,
        entity_overview_score=overall_sentiment_score_for_gauge,
        results_exist=(True if news_items_for_feed_dicts else False)
    )

# API endpoint for fetching filtered data for the dashboard
@bp.route('/api/filtered_report_data/<int:report_id>', methods=['POST'])
@login_required
def api_filtered_report_data(report_id):
    report = db.session.get(AnalysisReport, report_id)
    if report is None:
        return jsonify({'error': 'Report not found'}), 404

    is_author = report.user_id == current_user.id
    is_shared_with_current_user = db.session.query(report.shared_with_recipients.filter(User.id == current_user.id).exists()).scalar()

    if not is_author and not is_shared_with_current_user:
        return jsonify({'error': 'Permission denied'}), 403

    filters = request.json
    if not filters:
        return jsonify({'error': 'No filters provided'}), 400

    # Base query for news items of the current report
    query = report.news_items # This is a BaseQuery object because of lazy='dynamic'

    # Apply filters
    # Date range filter
    date_range_str = filters.get('date_range')
    if date_range_str:
        try:
            start_date_str, end_date_str = date_range_str.split(' to ')
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc) + timedelta(days=1) # end_date is exclusive
            query = query.filter(NewsItem.publication_date >= start_date, NewsItem.publication_date < end_date)
        except ValueError:
            return jsonify({'error': 'Invalid date range format. Use YYYY-MM-DD to YYYY-MM-DD'}), 400

    # Sentiment range filter (e.g., from -1 to +1)
    sentiment_min = filters.get('sentiment_min')
    sentiment_max = filters.get('sentiment_max')
    if sentiment_min is not None:
        query = query.filter(NewsItem.sentiment_score >= float(sentiment_min))
    if sentiment_max is not None:
        query = query.filter(NewsItem.sentiment_score <= float(sentiment_max))
    
    # Intent filter (exact match for now, could be 'contains' if intents are stored differently)
    # Assuming intents are stored as a JSON list string: '["News Report", "Opinion"]'
    intent_filter = filters.get('intent')
    if intent_filter:
        # This requires a LIKE query or a more advanced JSON query if DB supports it.
        # For SQLite, LIKE is the most straightforward for JSON arrays stored as strings.
        query = query.filter(NewsItem.intents.like(f'%"{intent_filter}"%'))

    # Keyword filter (search in keywords JSON list string)
    keyword_filter = filters.get('keyword')
    if keyword_filter:
        query = query.filter(NewsItem.keywords.like(f'%"{keyword_filter}"%'))
    
    # Source/Author filter (NewsItem doesn't have author/source field yet, this is a placeholder)
    # source_filter = filters.get('source')
    # if source_filter:
    #     query = query.filter(NewsItem.source.ilike(f'%{source_filter}%'))


    # Pagination
    page = filters.get('page', 1)
    per_page = filters.get('per_page', 10)
    
    # Order by publication date (descending, newest first), then by ID as a fallback
    paginated_news_items = query.order_by(NewsItem.publication_date.desc().nullslast(), NewsItem.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    news_items_data = [item.to_dict() for item in paginated_news_items.items]
    
    return jsonify({
        'news_items': news_items_data,
        'total_items': paginated_news_items.total,
        'current_page': paginated_news_items.page,
        'total_pages': paginated_news_items.pages,
        'has_next': paginated_news_items.has_next,
        'has_prev': paginated_news_items.has_prev
    })


# --- Sharing Routes (Updated for AnalysisReport) ---
@bp.route('/share_report/<int:report_id>', methods=['GET', 'POST'])
@login_required
def share_report(report_id):
    report = db.session.get(AnalysisReport, report_id)
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
        # Corrected check for list-based relationship:
        elif user_to_share_with in report.shared_with_recipients:
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
    # Verify ownership
    if not report or report.author.id != current_user.id:
        flash('Analysis report not found or you do not own this report.', 'danger')
        return redirect(url_for('main.results'))

    # Get unique users for the selection list - exclude current user
    # Use distinct query to ensure no duplicates
    available_users = db.session.execute(
        db.select(User).where(User.id != current_user.id).order_by(User.username)
    ).scalars().all()
    
    # Create form with unique user choices
    form = ManageSharingForm()
    form.users_to_share_with.choices = [(user.id, user.username) for user in available_users]

    if form.validate_on_submit():
        # Get current shared user IDs
        current_shared_ids = {user.id for user in report.shared_with_recipients}
        selected_ids = set(form.users_to_share_with.data)
        
        # Add new users
        ids_to_add = selected_ids - current_shared_ids
        for user_id_to_add in ids_to_add:
            user = db.session.get(User, user_id_to_add)
            if user: report.shared_with_recipients.append(user)
        
        # Remove deselected users
        ids_to_remove = current_shared_ids - selected_ids
        for user_id_to_remove in ids_to_remove:
            user = db.session.get(User, user_id_to_remove)
            if user: report.shared_with_recipients.remove(user)
            
        db.session.commit()
        flash('Sharing settings updated.', 'success')
        return redirect(url_for('main.results_dashboard', report_id=report_id))

    # Important: Set the selected values on GET requests
    if request.method == 'GET':
        form.users_to_share_with.data = [user.id for user in report.shared_with_recipients]
    
    return render_template('manage_sharing.html', title='Manage Sharing', form=form, report=report)


@bp.route('/remove_shared_user/<int:report_id>/<int:user_id>', methods=['POST'])
@login_required
def remove_shared_user(report_id, user_id):
    """
    Remove a shared user from the given analysis report.
    Only the report author can perform this action.
    """
    report = db.session.get(AnalysisReport, report_id)
    # Verify the report exists and current user is the author
    if not report or report.author.id != current_user.id:
        flash('Report not found or permission denied.', 'danger')
        return redirect(url_for('main.results'))

    user = db.session.get(User, user_id)
    # If the user is in the shared recipients, remove and commit
    if user and user in report.shared_with_recipients:
        report.shared_with_recipients.remove(user)
        db.session.commit()
        flash(f'Removed access for user {user.username}.', 'success')
    else:
        flash('User was not shared or already removed.', 'info')

    return redirect(url_for('main.manage_report_sharing', report_id=report_id))

@bp.route('/shared_with_me')
@login_required
def shared_with_me():
    # current_user.analysis_reports_shared_with_me is now a list
    reports_list = current_user.analysis_reports_shared_with_me
    # Sort the list in Python by timestamp
    sorted_reports = sorted(reports_list, key=lambda r: r.timestamp, reverse=True)
    return render_template('shared_with_me.html', title='Shared With Me', reports=sorted_reports)


@bp.route('/shared_report_details/<int:report_id>')
@login_required
def shared_report_details(report_id):
    # This route should probably just redirect to the main results_dashboard
    # The permission check is handled there.
    report = db.session.get(AnalysisReport, report_id)
    if report is None:
        flash('Shared report not found.', 'danger')
        return redirect(url_for('main.shared_with_me'))

    # Check if it's actually shared with the current user
    is_shared_with_current_user = db.session.query(report.shared_with_recipients.filter(User.id == current_user.id).exists()).scalar()
    
    if not is_shared_with_current_user:
        flash('This report is not shared with you or access has been revoked.', 'warning')
        return redirect(url_for('main.shared_with_me'))
        
    # If shared, show the main dashboard for this report
    return redirect(url_for('main.results_dashboard', report_id=report_id))

@bp.route('/visualization')
@login_required
def visualization():
    # Fetch all analysis reports for current user (trend by report)
    reports = AnalysisReport.query \
        .filter_by(user_id=current_user.id) \
        .order_by(AnalysisReport.timestamp) \
        .all()
    dates = [r.timestamp.strftime('%Y-%m-%d %H:%M') for r in reports]
    scores = [
    1 if (r.overall_sentiment_score or 0) > 0 
    else -1 if (r.overall_sentiment_score or 0) < 0 
    else 0
    for r in reports
]

    # Compute overall sentiment counts from news items
    items = db.session.query(NewsItem) \
        .join(NewsItem.analysis_report) \
        .filter(AnalysisReport.user_id == current_user.id) \
        .all()
    sentiment_counts_list = [
        sum(1 for i in items if i.sentiment_label.lower() == 'positive'),
        sum(1 for i in items if i.sentiment_label.lower() == 'neutral'),
        sum(1 for i in items if i.sentiment_label.lower() == 'negative'),
    ]

    return render_template(
        'visualization.html',
        dates=dates,
        scores=scores,
        sentiment_counts=sentiment_counts_list
    )

# Old /results route (from before AnalysisReport) is now /results_list
# Old /share_analysis and /manage_sharing are updated to /share_report and /manage_report_sharing
# Old /shared_results/<id> is now /shared_report_details/<id>