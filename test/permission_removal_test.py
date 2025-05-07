"""
Test for removing sharing permissions.
"""

from app import create_app, db
from app.models import User, Result
import sys
import random

app = create_app()

def test_remove_sharing():
    """Test removing sharing permissions"""
    with app.app_context():
        try:
            print("\n--- Permission removal test ---")
            
            # Create unique test users
            random_suffix = random.randint(1000, 9999)
            
            # Create test users with unique names
            user1_name = f"user1_{random_suffix}"
            user2_name = f"user2_{random_suffix}"
            
            user1 = User(username=user1_name, email=f"{user1_name}@example.com")
            user1.set_password("password")
            
            user2 = User(username=user2_name, email=f"{user2_name}@example.com")
            user2.set_password("password")
            
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            print(f"Created test users: {user1.username} and {user2.username}")
            
            # Create a result for user1
            result = Result(
                original_text="Test sentiment analysis for permission removal", 
                sentiment="Positive", 
                author=user1
            )
            db.session.add(result)
            db.session.commit()
            
            print(f"Created test result: {result.id}")
            
            # Share result with user2
            result.shared_with_recipients.add(user2)
            db.session.commit()
            
            # Test that user2 now sees 1 shared result
            shared_after = db.session.scalars(user2.results_shared_with_me.select()).all()
            print(f"After sharing, user2 can see {len(shared_after)} results")
            
            # Remove the sharing permission
            print("Removing sharing permission...")
            result.shared_with_recipients.remove(user2)
            db.session.commit()
            
            # Test that user2 now sees 0 shared results again
            shared_after_removal = db.session.scalars(user2.results_shared_with_me.select()).all()
            print(f"After removing permission, user2 can see {len(shared_after_removal)} results")
            
            if len(shared_after_removal) == 0:
                print("✅ Permission removal is working correctly!")
            else:
                print("❌ Permission removal failed - user2 can still see the result")
                
            return len(shared_after_removal) == 0
            
        except Exception as e:
            print(f"Test failed with error: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_remove_sharing()
    sys.exit(0 if success else 1)
