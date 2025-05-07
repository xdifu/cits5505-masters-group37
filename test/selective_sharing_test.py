"""
Comprehensive test for selective sharing functionality, ensuring User A can share with User B 
without User C seeing the shared data.
"""

from app import create_app, db
from app.models import User, Result
import sys
import random

app = create_app()

def test_selective_sharing():
    """Test selective sharing between multiple users"""
    with app.app_context():
        try:
            print("\n--- Selective sharing test ---")
            
            # Create unique test users with random suffix
            random_suffix = random.randint(1000, 9999)
            
            alice_name = f"alice_{random_suffix}"
            bob_name = f"bob_{random_suffix}"
            charlie_name = f"charlie_{random_suffix}"
            
            alice = User(username=alice_name, email=f"{alice_name}@example.com")
            alice.set_password("password")
            
            bob = User(username=bob_name, email=f"{bob_name}@example.com")
            bob.set_password("password")
            
            charlie = User(username=charlie_name, email=f"{charlie_name}@example.com")
            charlie.set_password("password")
            
            db.session.add_all([alice, bob, charlie])
            db.session.commit()
            
            print(f"Created test users: {alice.username}, {bob.username}, and {charlie.username}")
            
            # Create results for Alice
            result1 = Result(
                original_text="This is a positive analysis by Alice", 
                sentiment="Positive", 
                author=alice
            )
            
            result2 = Result(
                original_text="This is a negative analysis by Alice", 
                sentiment="Negative", 
                author=alice
            )
            
            db.session.add_all([result1, result2])
            db.session.commit()
            
            print(f"Created test results: {result1.id} and {result2.id}")
            
            # TEST 1: Verify all users initially see 0 shared results
            bob_results_before = db.session.scalars(bob.results_shared_with_me.select()).all()
            charlie_results_before = db.session.scalars(charlie.results_shared_with_me.select()).all()
            
            print(f"Before sharing: Bob sees {len(bob_results_before)} results, Charlie sees {len(charlie_results_before)} results")
            
            # TEST 2: Share result1 with Bob only
            print("Sharing result1 with Bob only...")
            result1.shared_with_recipients.add(bob)
            db.session.commit()
            
            # Verify Bob sees 1 result and Charlie still sees 0
            bob_results_after1 = db.session.scalars(bob.results_shared_with_me.select()).all()
            charlie_results_after1 = db.session.scalars(charlie.results_shared_with_me.select()).all()
            
            print(f"After sharing result1: Bob sees {len(bob_results_after1)} results, Charlie sees {len(charlie_results_after1)} results")
            
            # TEST 3: Share result2 with Charlie only
            print("Sharing result2 with Charlie only...")
            result2.shared_with_recipients.add(charlie)
            db.session.commit()
            
            # Verify Bob still sees 1 result and Charlie now sees 1 result
            bob_results_after2 = db.session.scalars(bob.results_shared_with_me.select()).all()
            charlie_results_after2 = db.session.scalars(charlie.results_shared_with_me.select()).all()
            
            print(f"After sharing result2: Bob sees {len(bob_results_after2)} results, Charlie sees {len(charlie_results_after2)} results")
            
            # TEST 4: Verify each user sees the correct result
            if bob_results_after2 and charlie_results_after2:
                bob_result_text = bob_results_after2[0].original_text
                charlie_result_text = charlie_results_after2[0].original_text
                
                print(f"Bob's shared result: '{bob_result_text}'")
                print(f"Charlie's shared result: '{charlie_result_text}'")
                
                if "positive" in bob_result_text and "negative" in charlie_result_text:
                    print("✅ Selective sharing is working correctly! Users see only results shared with them.")
                else:
                    print("❌ Selective sharing test failed: Users are not seeing the correct content.")
            else:
                print("❌ Selective sharing test failed: Missing expected shared results.")
            
            # TEST 5: Remove sharing permission for Bob
            print("\nTEST 5: Removing sharing permission for Bob...")
            result1.shared_with_recipients.remove(bob)
            db.session.commit()
            
            # Verify Bob now sees 0 results and Charlie still sees 1 result
            bob_results_after_removal = db.session.scalars(bob.results_shared_with_me.select()).all()
            charlie_results_after_removal = db.session.scalars(charlie.results_shared_with_me.select()).all()
            
            print(f"After removing Bob's access: Bob sees {len(bob_results_after_removal)} results, Charlie sees {len(charlie_results_after_removal)} results")
            
            if len(bob_results_after_removal) == 0 and len(charlie_results_after_removal) == 1:
                print("✅ Permission removal is working correctly! Bob can no longer see the result.")
            else:
                print("❌ Permission removal test failed: Bob still has access or Charlie lost access.")
            
            return True
            
        except Exception as e:
            print(f"Test failed with error: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_selective_sharing()
    sys.exit(0 if success else 1)
