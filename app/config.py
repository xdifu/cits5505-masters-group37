# app/config.py

class Config:
    SECRET_KEY = 'default-secret'
    WTF_CSRF_ENABLED = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False  

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False 
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"