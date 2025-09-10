 
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Basic Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'sentiment-analysis-advanced-secret-key')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Application Settings
    MAX_TEXT_LENGTH = 2000
    MAX_HISTORY_ITEMS = 50
    SESSION_TIMEOUT = timedelta(hours=24)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///sentiment_analysis.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Analysis Settings
    ENABLE_EMOTION_ANALYSIS = True
    ENABLE_TEXT_STATISTICS = True
    ENABLE_COMPARATIVE_ANALYSIS = True