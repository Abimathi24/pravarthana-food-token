import os
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    # Only initialize if not already initialized
    if not firebase_admin._apps:
        # Check if service account key exists
        service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY', 'serviceAccountKey.json')
        
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully.")
        else:
            print(f"WARNING: Firebase service account key not found at {service_account_path}.")
            print("Please add your serviceAccountKey.json to the root directory.")
            # We initialize a default app anyway for local testing without firebase if needed, 
            # or it will just crash when trying to access firestore without creds.
            # In a real scenario, you should provide the key.
            pass

def get_db():
    init_firebase()
    try:
        return firestore.client()
    except Exception as e:
        print(f"Error accessing Firestore: {e}")
        return None
