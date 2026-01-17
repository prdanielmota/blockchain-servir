import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao-mude-em-producao'
    
    # Database Config
    # If DATABASE_URL env var exists (Production), use it. Otherwise use local SQLite.
    # We replace 'postgres://' with 'postgresql://' because SQLAlchemy requires the latter, 
    # but some hosts (like Heroku/Railway) provide the former.
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///' + os.path.join(BASE_DIR, 'servir.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # System Config
    # IP/Domain to be used in links sent by the bot
    # In production, set BASE_URL env var to your https://app-name.railway.app
    BASE_URL = os.environ.get('BASE_URL') or "http://127.0.0.1:5001"

    # Security Config
    # API Key to protect the webhook endpoint
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET') or 'segredo-padrao-mude-no-env'
    
    # Cookie Security (Enable in Production)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True if os.environ.get('FLASK_ENV') == 'production' else False
    SESSION_COOKIE_SAMESITE = 'Lax'
