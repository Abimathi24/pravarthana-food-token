import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
    
    # Optional settings for admin dashboard
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@pravarthana.com')
