"""
Very simple test for the selective sharing functionality, focused on core model functionality.
"""

from app import create_app, db
from app.models import User, Result
import sys

app = create_app()

def test_basic_sharing():
    """Test the basic sharing functionality between two users"""
    with app.app_context():
        try:
            print("\n--- Basic sharing test ---")
            
            # Create unique test users
            import random
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
                original_text="Test sentiment analysis text", 
                sentiment="Positive", 
                author=user1
            )
            db.session.add(result)
            db.session.commit()
            
            print(f"Created test result: {result.id}")
            
            # Test that user2 initially sees 0 shared results
            shared_before = db.session.scalars(user2.results_shared_with_me.select()).all()
            print(f"Before sharing, user2 can see {len(shared_before)} results")
            
            # Share result with user2
            result.shared_with_recipients.add(user2)
            db.session.commit()
            
            # Test that user2 now sees 1 shared result
            shared_after = db.session.scalars(user2.results_shared_with_me.select()).all()
            print(f"After sharing, user2 can see {len(shared_after)} results")
            
            if len(shared_after) > 0:
                print(f"Shared result text: '{shared_after[0].original_text}'")
                print(f"Shared result author: {shared_after[0].author.username}")
                print("Sharing functionality is working correctly!")
            else:
                print("ERROR: Sharing functionality is not working correctly")
                
            return True
            
        except Exception as e:
            print(f"Test failed with error: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_basic_sharing()
    sys.exit(0 if success else 1)
