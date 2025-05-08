import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add other common configurations here

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app-dev.db')
    # Ensure the 'instance' folder exists for the SQLite DB
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:' # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False # Disable CSRF forms in tests for convenience
    SERVER_NAME = 'localhost.localdomain' # Added for url_for in tests
    APPLICATION_ROOT = '/'  # Added for url_for in tests
    PREFERRED_URL_SCHEME = 'http' # Added for url_for in tests

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    # Ensure the 'instance' folder exists for the SQLite DB
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    # Add other production-specific configs

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
