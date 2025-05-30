# Main entry point for the Flask application.
# This script imports the Flask app instance and runs the development server.

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file at the very beginning

from app import create_app
from config import DevelopmentConfig, ProductionConfig # Import specific configs
import os

# This 'app' instance is what Flask CLI (e.g., flask db commands) will discover
# Explicitly use DevelopmentConfig for CLI operations to ensure DB URI is set.
app = create_app(DevelopmentConfig)
# Debug print to check the URI when run.py is imported by Flask CLI
print(f"[CLI App Context] SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

if __name__ == '__main__':
    # This block executes when running 'python run.py' directly for the dev server
    selected_config = DevelopmentConfig
    if os.environ.get('FLASK_ENV') == 'production':
        selected_config = ProductionConfig
        print("Configuring server for Production.")
    else:
        # Default to DevelopmentConfig if FLASK_ENV is not 'production'
        print("Configuring server for Development.")
    
    server_app = create_app(selected_config)
    # Debug print for server execution
    print(f"[Server App Context] SQLALCHEMY_DATABASE_URI: {server_app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    is_debug_mode = server_app.config.get('DEBUG', False) # Get DEBUG from config
    server_app.run(debug=is_debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))