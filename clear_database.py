#!/usr/bin/env python
# filepath: /home/god/cits5505-masters-group37/clear_database.py
"""
Database Clearing Tool

************************************************************************************
** WARNING: DEVELOPMENT USE ONLY - DESTRUCTIVE OPERATION **
This script provides functionality to clear user data, analysis results,
and sharing relationships from the database by deleting rows from tables.
It preserves the database schema (table structures).
USE FLASK-MIGRATE (flask db upgrade/downgrade) FOR SCHEMA EVOLUTION.
This script is for quickly clearing data during development.
IT WILL WIPE DATA FROM TABLES.
************************************************************************************
"""

from app import create_app, db
import sqlalchemy as sa
from app.models import User, Result, result_shares

def clear_all_data():
    """
    Clear all user data, analysis results, and sharing relationships.
    
    This function performs the following operations:
    1. Deletes all sharing relationships
    2. Deletes all analysis results
    3. Deletes all users
    """
    print("WARNING: This will delete ALL users, results, and sharing data!")
    confirm = input("Are you sure you want to continue? [y/N]: ")
    
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return False
    
    app = create_app()
    
    with app.app_context():
        try:
            # Method 1: Using direct SQL DELETE statements (preserves table structure)
            # Delete in correct order to avoid foreign key constraint violations
            print("\nClearing database tables...")
            
            # First clear the association table (result_shares)
            db.session.execute(sa.text("DELETE FROM result_shares"))
            print("✓ Cleared sharing relationships")
            
            # Then clear the results table
            db.session.execute(sa.text("DELETE FROM result"))
            print("✓ Cleared analysis results")
            
            # Finally clear the users table
            db.session.execute(sa.text("DELETE FROM user"))
            print("✓ Cleared user accounts")
            
            # Commit the transaction
            db.session.commit()
            
            print(f"\nDatabase cleared successfully: {app.config['SQLALCHEMY_DATABASE_URI']}")
            return True
            
        except Exception as e:
            print(f"Error clearing database: {e}")
            db.session.rollback()
            return False

def clear_user_data(username=None):
    """
    Clear a specific user's data or allow selection from a list.
    
    Args:
        username (str, optional): Username to delete. If None, will show a list of users.
    """
    app = create_app()
    
    with app.app_context():
        # If no username provided, show list of users to choose from
        if not username:
            print("\nAvailable users:")
            users = db.session.query(User).all()
            
            if not users:
                print("No users found in the database.")
                return False
                
            for i, user in enumerate(users, 1):
                result_count = db.session.query(Result).filter_by(user_id=user.id).count()
                print(f"{i}. {user.username} ({user.email}) - {result_count} analysis results")
                
            try:
                choice = int(input("\nEnter user number to delete (0 to cancel): "))
                if choice == 0:
                    print("Operation cancelled.")
                    return False
                    
                if 1 <= choice <= len(users):
                    username = users[choice-1].username
                else:
                    print("Invalid selection.")
                    return False
            except ValueError:
                print("Invalid input.")
                return False
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete user '{username}' and all their data? [y/N]: ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return False
            
        try:
            # Find the user
            user = db.session.query(User).filter_by(username=username).first()
            
            if not user:
                print(f"User '{username}' not found.")
                return False
                
            # Get user ID for reference in queries
            user_id = user.id
                
            # 1. Delete sharing relationships involving this user
            # 1.1 Where user is recipient
            db.session.execute(
                sa.delete(result_shares).where(result_shares.c.recipient_id == user_id)
            )
            # 1.2 Where user is author of shared results
            authored_result_ids = db.session.query(Result.id).filter_by(user_id=user_id).all()
            authored_result_ids = [r[0] for r in authored_result_ids]
            if authored_result_ids:
                db.session.execute(
                    sa.delete(result_shares).where(result_shares.c.result_id.in_(authored_result_ids))
                )
                
            # 2. Delete user's analysis results
            db.session.execute(sa.delete(Result).where(Result.user_id == user_id))
            
            # 3. Delete the user
            db.session.execute(sa.delete(User).where(User.id == user_id))
            
            # Commit the transaction
            db.session.commit()
            
            print(f"User '{username}' and all their data successfully deleted.")
            return True
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("\nDatabase Clearing Tool")
    print("=====================\n")
    
    print("Select operation:")
    print("1. Clear all users and data")
    print("2. Clear a specific user's data")
    print("3. Exit")
    
    choice = input("\nEnter option number: ")
    
    if choice == '1':
        success = clear_all_data()
    elif choice == '2':
        success = clear_user_data()
    else:
        print("Operation cancelled.")
        exit(0)
    
    if success:
        print("\n✓ Operation completed successfully!")
    else:
        print("\n✗ Operation failed or was cancelled.")
