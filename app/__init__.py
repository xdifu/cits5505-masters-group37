# Initializes the Flask application and loads necessary configurations.
# This file acts as the package constructor for the 'app' module.

import os
from flask import Flask
from dotenv import load_dotenv

def create_app():
    """
    Factory function to create and configure the Flask application instance.

    Loads environment variables, initializes Flask, and registers blueprints/routes.

    Returns:
        Flask: The configured Flask application instance.
    """
    # Load environment variables from a .env file if it exists.
    # This is useful for managing configuration settings like API keys.
    load_dotenv()

    # Create the Flask application instance.
    # __name__ helps Flask locate templates and static files relative to this module.
    app = Flask(__name__)

    # Set a secret key for session management and CSRF protection (though not used in this minimal version).
    # It's important to set this for security in real applications.
    # Use an environment variable or generate a strong random key.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_secret_key_for_dev')

    # Import and register routes from the routes module.
    # We import here to avoid circular dependencies.
    with app.app_context():
        from . import routes

    return app