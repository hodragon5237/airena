import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json
import base64

firebase_service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if not firebase_service_account:
    raise ValueError("FIREBASE_SERVICE_ACCOUNT is not set in environment variables")
service_account_info = json.loads(base64.b64decode(firebase_service_account).decode('utf-8'))
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

db = firestore.client()