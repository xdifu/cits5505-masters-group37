"""
Test script to verify the sharing functionality models and relationships.
This script creates test users and results, then tests sharing relationships.
"""

from app import create_app, db
from app.models import User, Result
import sys

app = create_app()

def test_sharing():
    with app.app_context():
        print("Cleaning up any existing test data...")
        # Delete test users if they exist
        User.query.filter(User.username.in_(['test_user1', 'test_user2'])).delete()
        db.session.commit()
        
        print("Creating test users...")
        # Create test users
        user1 = User(username='test_user1', email='test1@example.com')
        user1.set_password('password')
        user2 = User(username='test_user2', email='test2@example.com')
        user2.set_password('password')
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        print("Creating test result...")
        # Create a test result for user1
        result = Result(original_text="This is a test result", sentiment="Positive", author=user1)
        db.session.add(result)
        db.session.commit()
        
        print("Testing sharing relationship...")
        # Test sharing the result with user2
        print(f"Before sharing, shared with {result.shared_with_recipients.count()} users")
        result.shared_with_recipients.add(user2)
        db.session.commit()
        print(f"After sharing, shared with {result.shared_with_recipients.count()} users")
        
        # Verify user2 can see the shared result
        shared_results_for_user2 = user2.results_shared_with_me.all()
        print(f"User2 can see {len(shared_results_for_user2)} shared results")
        if shared_results_for_user2:
            result_data = shared_results_for_user2[0]
            print(f"Shared result text: {result_data.original_text}")
            print(f"Shared result sentiment: {result_data.sentiment}")
            print(f"Shared result author: {result_data.author.username}")
        
        print("Test completed successfully!")
        return True

if __name__ == "__main__":
    success = test_sharing()
    sys.exit(0 if success else 1)
