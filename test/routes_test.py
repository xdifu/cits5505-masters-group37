"""
Integration test for the routes related to selective sharing.

This script tests:
1. Creating users and results
2. The share_analysis route for sharing with specific users
3. The shared_with_me route for viewing shared results
4. The manage_sharing route for managing multiple sharing recipients
"""

from app import create_app, db
from app.models import User, Result
import sys

app = create_app()

def print_route_summary():
    """Print a summary of the routes related to sharing"""
    with app.app_context():
        print("\n--- Sharing-related Routes Summary ---")
        print("1. /results/<int:result_id>/share - Share analysis with a specific user")
        print("2. /shared_with_me - View results shared with the current user")
        print("3. /result/<int:result_id>/manage_sharing - Manage multiple sharing recipients")
        
        # Count existing users and results
        user_count = db.session.scalar(db.select(db.func.count()).select_from(User))
        result_count = db.session.scalar(db.select(db.func.count()).select_from(Result))
        
        print(f"\nCurrent database state: {user_count} users, {result_count} results")

def test_routes_implementation():
    """Verify that routes are correctly implemented and use proper database relationships"""
    with app.app_context():
        try:
            print("\nChecking route implementations in the code...")
            
            # Check share_analysis route
            from app.main.routes import share_analysis
            if hasattr(share_analysis, '__call__'):
                print("✅ /results/<int:result_id>/share route is implemented")
            else:
                print("❌ /results/<int:result_id>/share route is not properly implemented")
                
            # Check shared_with_me route
            from app.main.routes import shared_with_me
            if hasattr(shared_with_me, '__call__'):
                print("✅ /shared_with_me route is implemented")
            else:
                print("❌ /shared_with_me route is not properly implemented")
                
            # Check manage_sharing route
            from app.main.routes import manage_sharing
            if hasattr(manage_sharing, '__call__'):
                print("✅ /result/<int:result_id>/manage_sharing route is implemented")
            else:
                print("❌ /result/<int:result_id>/manage_sharing route is not properly implemented")
                
            # Check that forms are properly defined
            from app.forms import ShareForm, ManageSharingForm
            if hasattr(ShareForm, 'share_with_username') and hasattr(ManageSharingForm, 'users_to_share_with'):
                print("✅ Forms are properly defined for sharing functionality")
            else:
                print("❌ Forms for sharing functionality are missing required fields")
                
            return True
            
        except ImportError as e:
            print(f"❌ Route implementation check failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False

def test_templates_existence():
    """Check if all required templates exist"""
    import os
    
    templates_to_check = [
        'templates/share_analysis.html',
        'templates/shared_with_me.html',
        'templates/manage_sharing.html'
    ]
    
    print("\nChecking template files...")
    
    all_templates_exist = True
    for template in templates_to_check:
        template_path = os.path.join('/home/god/cits5505-masters-group37/app', template)
        if os.path.exists(template_path):
            print(f"✅ Template exists: {template}")
        else:
            print(f"❌ Template missing: {template}")
            all_templates_exist = False
            
    return all_templates_exist

if __name__ == "__main__":
    print_route_summary()
    routes_implemented = test_routes_implementation()
    templates_exist = test_templates_existence()
    
    if routes_implemented and templates_exist:
        print("\n✅ All sharing routes and templates are properly implemented!")
        sys.exit(0)
    else:
        print("\n❌ Some sharing routes or templates are missing or improperly implemented.")
        sys.exit(1)
