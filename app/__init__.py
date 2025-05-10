# Initializes the Flask application, extensions, and loads configurations.

import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime # Import datetime for context processor
from config import config # Import the config dictionary

# Load environment variables first
load_dotenv()

# Initialize extensions without app instance
db = SQLAlchemy()
login_manager = LoginManager()
# Set the login view endpoint (using blueprint name 'auth' and function 'login')
login_manager.login_view = 'auth.login'
# Set the message category for login required messages
login_manager.login_message_category = 'info'


def create_app(config_name='default'): # Changed parameter name and default
    """
    Factory function to create and configure the Flask application instance.

    Loads environment variables, initializes Flask, configures extensions,
    and registers blueprints.

    Args:
        config_name (str): The name of the configuration to use (e.g., 'development', 'testing').

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)

    # --- Configuration ---
    # Load configuration from config.py using config_name
    app.config.from_object(config[config_name])

    # Enable Jinja2 'do' extension
    app.jinja_options['extensions'] = ['jinja2.ext.do'] # Add DoExtension

    # --- Initialize Extensions with App ---
    db.init_app(app)
    login_manager.init_app(app)

    # --- User Loader for Flask-Login ---
    # Import User model here to avoid circular imports at the top level
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        """Callback function used by Flask-Login to load a user by ID."""
        # user_id is stored as a string in the session, convert to int for query
        return db.session.get(User, int(user_id))

    # --- Register Blueprints ---
    # Import blueprints here to avoid circular imports
    from .auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .main.routes import bp as main_bp
    app.register_blueprint(main_bp) # Register main blueprint without prefix

    # --- Context Processor ---
    # Make variables available to all templates
    @app.context_processor
    def inject_now():
        """Injects the current year into template context."""
        return {'now': datetime.utcnow()}


    return app

# Import models at the bottom to avoid circular dependencies with 'db'
# Although not strictly necessary with the factory pattern, it's good practice.
from . import models