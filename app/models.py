# Defines the database models for the application using SQLAlchemy.
# Includes models for Users, their sentiment analysis reports (AnalysisReport),
# and individual news items within those reports (NewsItem).

from datetime import datetime, timezone # Import datetime for timestamping
from typing import Optional, List # For type hinting optional relationships and lists
import sqlalchemy as sa # Core SQLAlchemy library
import sqlalchemy.orm as so # SQLAlchemy ORM components
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
from flask_login import UserMixin # Provides default implementations for Flask-Login user methods
import json # For handling JSON data in text fields

# Import the db instance initialized in app/__init__.py
from app import db, login_manager

# Association table for AnalysisReport sharing
# Renamed from result_shares to analysis_report_shares
analysis_report_shares = db.Table('analysis_report_shares',
    db.Column('analysis_report_id', sa.Integer, db.ForeignKey('analysis_report.id'), primary_key=True),
    db.Column('recipient_id', sa.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """
    Represents a user in the application.
    Includes authentication fields and relationship to analysis reports.
    Inherits from UserMixin for Flask-Login integration.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True, nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True, nullable=False)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=False)

    # Renamed from authored_results to authored_analysis_reports
    # Relationship to AnalysisReport (reports authored by the user)
    authored_analysis_reports: so.WriteOnlyMapped['AnalysisReport'] = so.relationship(
        back_populates='author', lazy='select',
        cascade="all, delete-orphan", passive_deletes=True
    )

    # Renamed from results_shared_with_me to analysis_reports_shared_with_me
    # AnalysisReports shared with this user by others
    analysis_reports_shared_with_me: so.WriteOnlyMapped['AnalysisReport'] = so.relationship(
        secondary=analysis_report_shares,
        primaryjoin=(analysis_report_shares.c.recipient_id == id),
        # Ensure AnalysisReport.id is used in secondaryjoin if class name changed
        secondaryjoin="analysis_report_shares.c.analysis_report_id == AnalysisReport.id",
        back_populates='shared_with_recipients',
        lazy='dynamic',
        passive_deletes=True
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# Renamed from Result to AnalysisReport
class AnalysisReport(db.Model):
    __tablename__ = 'analysis_report' # Explicitly define table name
    """
    Represents a single sentiment analysis report/session.
    This report aggregates data from multiple NewsItem entries.
    """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128)) # Optional name for the report
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc)) # Added timestamp
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), index=True) # Added user_id

    author: so.Mapped['User'] = so.relationship(back_populates='authored_analysis_reports') # Added author relationship

    # News items associated with this report
    news_items: so.WriteOnlyMapped['NewsItem'] = so.relationship(
        back_populates='analysis_report', cascade="all, delete-orphan"
    )

    # Recipients with whom this report is shared
    shared_with_recipients: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=analysis_report_shares,
        primaryjoin=(analysis_report_shares.c.analysis_report_id == id),
        secondaryjoin=(analysis_report_shares.c.recipient_id == User.id), # Corrected secondaryjoin
        back_populates='analysis_reports_shared_with_me',
        lazy='dynamic',
        passive_deletes=True # Added passive_deletes
    )
    
    # Add the missing 'shared' column
    shared: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, nullable=False)

    # Aggregated sentiment data for the entire report
    overall_sentiment_label: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64)) # e.g., 'Positive', 'Neutral', 'Mixed'
    overall_sentiment_score: so.Mapped[Optional[float]] = so.mapped_column(sa.Float) # Average score from -1 to +1

    # JSON fields to store data for dashboard components
    # Stores Top-5 intents for the pie chart: e.g., '{"News Report": 0.4, ...}'
    aggregated_intents_json: so.Mapped[Optional[str]] = so.mapped_column(sa.Text) 
    # Stores Top-20 keywords for word cloud: e.g., '[{"text": "economy", "count": 20, "avg_sentiment": 0.3}, ...]    
    aggregated_keywords_json: so.Mapped[Optional[str]] = so.mapped_column(sa.Text) # Added field
    # Stores data for sentiment trend chart: e.g., '{"overall": [{"date": "YYYY-MM-DD", "score": 0.5}, ...], "keyword1": [...] }'
    sentiment_trend_json: so.Mapped[Optional[str]] = so.mapped_column(sa.Text) # Added field


class NewsItem(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    original_text: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    # Sentiment analysis results from OpenAI
    sentiment_label: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False) # Positive, Neutral, Negative
    sentiment_score: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False) # -1.0 to +1.0
    
    # Store intents as a JSON string list, e.g., '["News Report", "Market Analysis"]'
    intents_json: so.Mapped[Optional[str]] = so.mapped_column(sa.Text) 
    
    # Store keywords with their individual sentiment scores as a JSON string
    # e.g., '[{"text": "economy", "sentiment_score": 0.5}, {"text": "growth", "sentiment_score": 0.7}]'
    keywords_with_sentiment_json: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    # Estimated publication date from analysis
    publication_date: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime) 
    
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    # Foreign Key to link back to the AnalysisReport
    analysis_report_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('analysis_report.id'), index=True)
    analysis_report: so.Mapped['AnalysisReport'] = so.relationship(back_populates='news_items')

    def __repr__(self):
        return f'<NewsItem {self.id} Sentiment: {self.sentiment_label}>'

    # Helper methods to get/set intents and keywords as Python lists
    def get_intents(self) -> list:
        if self.intents_json:
            try:
                return json.loads(self.intents_json)
            except json.JSONDecodeError:
                return []
        return []

    def set_intents(self, intents_list: list):
        self.intents_json = json.dumps(intents_list)

    def get_keywords(self) -> list:
        if self.keywords_with_sentiment_json:
            try:
                return json.loads(self.keywords_with_sentiment_json)
            except json.JSONDecodeError:
                return []
        return []

    def set_keywords(self, keywords_list: list):
        self.keywords_with_sentiment_json = json.dumps(keywords_list)

    def to_dict(self):
        return {
            "id": self.id,
            "original_text": self.original_text,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "sentiment_score": self.sentiment_score,
            "sentiment_label": self.sentiment_label,
            "intents": self.get_intents(),
            "keywords": self.get_keywords(),
            "report_id": self.analysis_report_id
        }


@login_manager.user_loader
def load_user(id):
    # Ensure to query User by integer ID
    return db.session.get(User, int(id)) # Use db.session.get for SQLAlchemy 2.0 style if preferred