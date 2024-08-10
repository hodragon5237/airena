from flask import Flask
from dotenv import load_dotenv
import os
import routes
from config import Config
import firebase_admin
from firebase_admin import credentials
from flask_cors import CORS
from datetime import timedelta
import json
import base64
from flask_talisman import Talisman
import logging

logging.basicConfig(filename='app.log', level=logging.ERROR)

# .env 파일에서 환경 변수 로드
load_dotenv()

def create_app():

    app = Flask(__name__)
    CORS(app)
    app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
    app.config.from_object(Config)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_TYPE'] = 'filesystem'

    # 블루프린트 등록
    app.register_blueprint(routes.main_bp)

    # Talisman 설정 추가
    Talisman(app, content_security_policy=csp, force_https=False)

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}")
        return "An internal error occurred", 500

    return app

csp = {
    'default-src': [
        "'self'",
        'https://cdnjs.cloudflare.com',
        'https://translate.google.com',
        'https://translate.googleapis.com',
        'https://translate-pa.googleapis.com',
        'https://www.google.com',
        'https://fonts.googleapis.com',
        'https://fonts.gstatic.com',
        'https://www.gstatic.com',
    ],
    'script-src': [
        "'self'",
        'https://cdnjs.cloudflare.com',
        'https://translate.google.com',
        'https://translate.googleapis.com',
        'https://translate-pa.googleapis.com',
        'https://www.google.com',
        'https://www.gstatic.com',
        "'unsafe-inline'",
        "'unsafe-eval'"
    ],
    'style-src': [
        "'self'",
        'https://cdnjs.cloudflare.com',
        'https://translate.google.com',
        'https://translate.googleapis.com',
        'https://fonts.googleapis.com',
        'https://www.gstatic.com',
        "'unsafe-inline'"
    ],
    'font-src': [
        "'self'",
        'data:',
        'https:',
        'https://fonts.gstatic.com',
    ],
    'img-src': ["'self'", 'data:', 'https:', 'http://translate.google.com'],
    'connect-src': [
        "'self'", 
        'https://translate.googleapis.com',
        'https://translate-pa.googleapis.com'
    ],
}

if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=8080)

# # Local
# if __name__ == "__main__":
#     app = create_app()
#     app.run(debug=True, host='127.0.0.1', port=5000)