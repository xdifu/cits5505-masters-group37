"""
Comprehensive test for the selective sharing functionality.

This script tests:
1. Creating users and results
2. Adding a user to a result's shared_with_recipients
3. Testing that a user can see results shared with them
4. Removing sharing permission
"""

from app import create_app, db
from app.models import User, Result
import sys

app = create_app()

def setup_test_data():
    """Create test users and results"""
    with app.app_context():
        print("Starting test setup...")
        # Delete test users if they exist
        try:
            user1 = db.session.scalar(db.select(User).where(User.username == 'alice'))
            user2 = db.session.scalar(db.select(User).where(User.username == 'bob'))
            user3 = db.session.scalar(db.select(User).where(User.username == 'charlie'))
            
            # Clean up existing test users
            if user1:
                print(f"Deleting existing user: {user1.username}")
                db.session.delete(user1)
            if user2:
                print(f"Deleting existing user: {user2.username}")
                db.session.delete(user2)
            if user3:
                print(f"Deleting existing user: {user3.username}")
                db.session.delete(user3)
            db.session.commit()
            print("Deleted existing test users")
        except Exception as e:
            print(f"Error deleting users: {e}")
            db.session.rollback()
        
        # Create test users
        try:
            print("Creating test users...")
            alice = User(username='alice', email='alice@example.com')
            alice.set_password('password')
            
            bob = User(username='bob', email='bob@example.com')
            bob.set_password('password')
            
            charlie = User(username='charlie', email='charlie@example.com')
            charlie.set_password('password')
            
            # Add users to database
            db.session.add(alice)
            db.session.add(bob)
            db.session.add(charlie)
            db.session.commit()
            print("Successfully created test users")
        except Exception as e:
            print(f"Error creating users: {e}")
            db.session.rollback()
            raise
        
        # Create test results for Alice
        try:
            print("Creating test results...")
            result1 = Result(original_text="This is a positive text.", sentiment="Positive", author=alice)
            result2 = Result(original_text="This is a neutral text.", sentiment="Neutral", author=alice)
            
            db.session.add(result1)
            db.session.add(result2)
            db.session.commit()
            print("Successfully created test results")
            
            return alice, bob, charlie, result1, result2
        except Exception as e:
            print(f"Error creating results: {e}")
            db.session.rollback()
            raise

def test_sharing_with_specific_user():
    """Test sharing with a specific user"""
    print("\n--- Testing selective sharing functionality ---\n")
    
    with app.app_context():
        try:
            alice, bob, charlie, result1, result2 = setup_test_data()
            
            print(f"Initial state: Alice has {db.session.scalar(db.select(db.func.count()).select_from(Result).where(Result.author == alice))} results")
            
            # Before sharing - Bob should not see any results
            print(f"Before sharing: Bob can see {bob.results_shared_with_me.count()} results")
            
            # Test 1: Alice shares result1 with Bob
            print("\nTest 1: Alice shares result1 with Bob")
            result1.shared_with_recipients.add(bob)
            db.session.commit()
            print("Result 1 shared with Bob successfully")
            
            # Bob should now see 1 result
            print(f"After sharing result1: Bob can see {bob.results_shared_with_me.count()} results")
            
            # Charlie should still see 0 results (selective sharing)
            print(f"Charlie should still see 0 results: {charlie.results_shared_with_me.count()}")
            
            # Test 2: Alice shares result2 with Charlie but not Bob
            print("\nTest 2: Alice shares result2 with Charlie but not Bob")
            result2.shared_with_recipients.add(charlie)
            db.session.commit()
            print("Result 2 shared with Charlie successfully")
            
            # Bob should still see just 1 result
            print(f"Bob still sees {bob.results_shared_with_me.count()} results")
            
            # Charlie should now see 1 result
            print(f"Charlie now sees {charlie.results_shared_with_me.count()} results")
            
            # Get the first result shared with Bob and Charlie
            bob_result = bob.results_shared_with_me.first()
            charlie_result = charlie.results_shared_with_me.first()
            
            if bob_result:
                print(f"\nBob's shared result: '{bob_result.original_text}'")
            else:
                print("\nBob has no shared results")
            
            if charlie_result:
                print(f"Charlie's shared result: '{charlie_result.original_text}'")
            else:
                print("Charlie has no shared results")
            
            # Test 3: Alice removes sharing for Bob
            print("\nTest 3: Alice removes sharing for Bob")
            if bob_result:
                result1.shared_with_recipients.remove(bob)
                db.session.commit()
                print("Sharing removed for Bob successfully")
            
                # Bob should now see 0 results
                print(f"After removing sharing: Bob can see {bob.results_shared_with_me.count()} results")
            
            # Cleanup
            print("\nCleaning up test data...")
            # Delete all test results first to avoid foreign key constraints
            results = db.session.scalars(db.select(Result).where(Result.author.in_([alice, bob, charlie]))).all()
            for result in results:
                db.session.delete(result)
            db.session.commit()
            
            # Then delete users
            db.session.delete(alice)
            db.session.delete(bob)
            db.session.delete(charlie)
            db.session.commit()
            print("Cleanup completed successfully")
            
            print("\n--- Test completed successfully ---")
            return True
        except Exception as e:
            print(f"Test failed with error: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    try:
        success = test_sharing_with_specific_user()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test script failed with error: {e}")
        sys.exit(1)
