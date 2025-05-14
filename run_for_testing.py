# Simple script to run the Flask application for testing
import os
import sys
from app import create_app, db
from app.models import User, AnalysisReport  # Correct model imports
from config import TestingConfig

# Create an app instance with testing configuration
app = create_app(TestingConfig)

@app.before_first_request
def initialize_test_db():
    """Initialize the database with test data on first request"""
    print("Initializing test database...")
    with app.app_context():
        db.create_all()
        # Create a test user if it doesn't exist
        if User.query.filter_by(username='testuser').first() is None:
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            print("Created test user: testuser/password123")

if __name__ == '__main__':
    print("=" * 80)
    print("Starting Flask application for testing...")
    print(f"Server will be available at: http://localhost:5000/")
    print(f"Test user credentials: testuser/password123")
    print("=" * 80)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
