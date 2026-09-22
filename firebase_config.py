import firebase_admin
from firebase_admin import credentials, firestore, auth
from config import Config
import os

_db = None

def init_firebase():
    global _db
    if not firebase_admin._apps:
        cred_path = Config.FIREBASE_CREDENTIALS_PATH
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
            print("Firebase Initialized Successfully.")
        else:
            print(f"WARNING: Firebase credentials not found at {cred_path}.")
            
def get_db():
    global _db
    if _db is None:
        init_firebase()
    return _db
