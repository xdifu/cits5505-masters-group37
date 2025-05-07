"""
Simpler test for the selective sharing functionality, focused just on the core model functionality.
"""

from app import create_app, db
from app.models import User, Result, result_shares
import sys
import sqlalchemy as sa

app = create_app()

def test_sharing_basics():
    """Basic test to ensure the sharing model is working correctly"""
    with app.app_context():
        print("\n--- Testing basic sharing functionality ---\n")
        
        try:
            # Clean up any existing test data using SQL directly to avoid ORM problems
            print("Cleaning up any existing test data...")
            
            # Locate test user IDs
            test_alice = db.session.scalar(sa.select(User).where(User.username == 'test_alice'))
            test_bob = db.session.scalar(sa.select(User).where(User.username == 'test_bob'))
            
            user_ids = []
            if test_alice:
                user_ids.append(test_alice.id)
            if test_bob:
                user_ids.append(test_bob.id)
                
            # If we found test users, clean up all related data
            if user_ids:
                # First remove entries from the association table
                db.session.execute(
                    sa.delete(result_shares).where(
                        (result_shares.c.recipient_id.in_(user_ids)) | 
                        (sa.exists().where(
                            sa.select(Result).where(
                                (Result.id == result_shares.c.result_id) & 
                                (Result.user_id.in_(user_ids))
                            )
                        ))
                    )
                )
                
                # Delete results authored by test users
                db.session.execute(
                    sa.delete(Result).where(Result.user_id.in_(user_ids))
                )
                
                # Finally delete the test users
                db.session.execute(
                    sa.delete(User).where(User.id.in_(user_ids))
                )
                
                db.session.commit()
                print("Cleaned up existing test data")
            
            # Create test users
            alice = User(username='test_alice', email='test_alice@example.com')
            alice.set_password('password')
            
            bob = User(username='test_bob', email='test_bob@example.com')
            bob.set_password('password')
            
            db.session.add(alice)
            db.session.add(bob)
            db.session.commit()
            
            print(f"Created test users: {alice.username} and {bob.username}")
            
            # Create a test result
            result = Result(
                original_text="Test sentiment analysis", 
                sentiment="Positive", 
                author=alice
            )
            db.session.add(result)
            db.session.commit()
            
            print(f"Created test result with id: {result.id}")
            
            # Check initial state
            initial_results = db.session.scalars(bob.results_shared_with_me.select()).all()
            print(f"Initially, bob can see {len(initial_results)} results")
            
            # Share the result with bob
            print("Sharing the result with bob...")
            result.shared_with_recipients.add(bob)
            db.session.commit()
            
            # Check if bob can see the shared result
            shared_results = db.session.scalars(bob.results_shared_with_me.select()).all()
            print(f"After sharing, bob can see {len(shared_results)} results")
            
            # Get the shared result
            shared_result = db.session.scalar(bob.results_shared_with_me.select().limit(1))
            if shared_result:
                print(f"Bob can see result: {shared_result.original_text} (sentiment: {shared_result.sentiment})")
                print(f"The result was authored by: {shared_result.author.username}")
            else:
                print("Error: Bob cannot see any shared results")
            
            # Clean up using SQL directly
            print("Cleaning up...")
            user_ids = [alice.id, bob.id]
            result_id = result.id
            
            # First remove entries from the association table
            db.session.execute(
                sa.delete(result_shares).where(
                    (result_shares.c.recipient_id.in_(user_ids)) | 
                    (result_shares.c.result_id == result_id)
                )
            )
            
            # Delete the result
            db.session.execute(
                sa.delete(Result).where(Result.id == result_id)
            )
            
            # Finally delete the test users
            db.session.execute(
                sa.delete(User).where(User.id.in_(user_ids))
            )
            
            db.session.commit()
            
            print("\n--- Test completed successfully ---")
            return True
            
        except Exception as e:
            print(f"Test failed with error: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_sharing_basics()
    sys.exit(0 if success else 1)
