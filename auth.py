from flask import Blueprint, session, redirect, url_for, flash, request, render_template
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
from firebase_admin import firestore
import base64
import json
from tempfile import NamedTemporaryFile
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import requests

# Google OAuth 설정
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid']

def create_flow():
    client_secrets_json = os.environ.get('CLIENT_SECRETS_JSON')
    if not client_secrets_json:
        raise ValueError("CLIENT_SECRETS_JSON is not set in the environment")
    
    decoded_secrets = base64.b64decode(client_secrets_json).decode('utf-8')
    
    client_secrets_dict = json.loads(decoded_secrets)

    with NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        json.dump(client_secrets_dict, temp_file)
        temp_file_path = temp_file.name

    flow = Flow.from_client_secrets_file(
            temp_file_path,
            scopes=SCOPES,
            redirect_uri=os.environ.get('REDIRECT_URI', "http://127.0.0.1:5000/auth/callback")
        )

    os.unlink(temp_file_path)
    return flow

# def auth_google():
#     authorization_url, state = flow.authorization_url(
#         access_type='offline',
#         include_granted_scopes='true',
#         prompt='consent'
#     )
#     session['state'] = state
#     return redirect(authorization_url)

def callback():
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # 개발 환경에서 HTTP를 허용
    flow = create_flow()
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Google API를 사용하여 사용자 정보 가져오기
    userinfo_service = build('oauth2', 'v2', credentials=credentials)
    user_info = userinfo_service.userinfo().get().execute()

    session.permanent = True  # 세션을 영구적으로 설정
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'email': user_info.get('email')
    }
    session['google_id'] = user_info.get('id')  # Google ID를 세션에 저장
    session['name'] = user_info.get('name')  # 사용자 이름을 세션에 저장
    session['email'] = user_info.get('email')  # 사용자 이메일을 세션에 저장

    return redirect(url_for('main.index'))

def verify_recaptcha(recaptcha_response):
    secret_key = os.getenv('RECAPTCHA_SECRET_KEY')
    payload = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    result = response.json()
    return result.get('success', False) and result.get('score', 0) >= 0.5  # 점수 기준 설정

def login():
    recaptcha_response = request.form.get('g-recaptcha-response')
    if not verify_recaptcha(recaptcha_response):
        flash('reCAPTCHA verification failed. Please try again.', 'error')
        return redirect(url_for('main.index'))
    
    flow = create_flow()
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
    session['state'] = state
    return redirect(authorization_url)

def logout():
    if 'credentials' in session:
        del session['credentials']
    return redirect(url_for('main.index'))

def refresh_token_if_needed():
    if 'credentials' in session:
        credentials_dict = session['credentials'].copy()
        credentials_dict.pop('email', None)  # email 키를 제거
        credentials = Credentials(**credentials_dict)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            session['credentials'] = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }