import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS')
    # GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    CLIENT_SECRETS_FILE = os.environ.get('CLIENT_SECRETS_FILE')
    # DEBUG = os.environ.get('FLASK_ENV') == 'development'