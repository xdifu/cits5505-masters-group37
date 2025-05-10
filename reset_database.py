#!/usr/bin/env python
# filepath: /home/god/cits5505-masters-group37/reset_database.py
"""
Database Reset Tool

************************************************************************************
** WARNING: DEVELOPMENT USE ONLY - DESTRUCTIVE OPERATION **
This script completely resets the database by dropping all tables and recreating them
based on the current models (db.drop_all(), db.create_all()).
IT BYPASSES THE FLASK-MIGRATE/ALEMBIC MIGRATION HISTORY.
USE FLASK-MIGRATE (flask db upgrade/downgrade) FOR SCHEMA EVOLUTION.
This script is for quickly resetting to a clean slate during development if needed,
but be aware that it will WIPE ALL DATA and your database will NOT be in sync
with migration history afterwards. You might need to re-stamp or re-initialize
migrations if you use this and then want to use Flask-Migrate.
************************************************************************************
"""

from app import create_app, db

def reset_database():
    """
    Reset the entire database by dropping all tables and recreating them.
    
    This is more drastic than just clearing data, as it will reset any schema
    changes or migrations that have been applied.
    """
    print("WARNING: This will RESET the ENTIRE database and ALL DATA WILL BE LOST!")
    print("This operation is NOT REVERSIBLE!")
    
    confirm = input("Are you sure you want to continue? Type 'RESET' to confirm: ")
    
    if confirm != 'RESET':
        print("Operation cancelled.")
        return False
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables
            print("\nDropping all database tables...")
            db.drop_all()
            print("✓ All tables dropped")
            
            # Recreate all tables
            print("\nRecreating database tables...")
            db.create_all()
            print("✓ All tables recreated")
            
            print(f"\nDatabase has been completely reset: {app.config['SQLALCHEMY_DATABASE_URI']}")
            return True
            
        except Exception as e:
            print(f"Error resetting database: {e}")
            return False

if __name__ == "__main__":
    print("\nDatabase Reset Tool")
    print("=================\n")
    
    print("This tool will COMPLETELY RESET the database by:")
    print("1. Dropping all tables")
    print("2. Recreating all tables with empty data")
    print("\nUnlike clear_database.py which only removes data but keeps tables,")
    print("this will reset the entire database structure.")
    
    choice = input("\nDo you want to continue? [y/N]: ")
    
    if choice.lower() == 'y':
        success = reset_database()
        
        if success:
            print("\n✓ Database successfully reset!")
        else:
            print("\n✗ Database reset failed or was cancelled.")
    else:
        print("Operation cancelled.")
