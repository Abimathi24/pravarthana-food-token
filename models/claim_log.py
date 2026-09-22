from datetime import datetime
from pymongo import DESCENDING

class ClaimLogModel:
    def __init__(self, db):
        self.collection = db.claim_logs
        self.collection.create_index([("scanned_at", DESCENDING)])

    def log_scan(self, qr_token, registration_id, action, scanner_email):
        log_doc = {
            "qr_token": qr_token,
            "registration_id": registration_id,
            "action": action, # 'SUCCESS', 'ALREADY_CLAIMED', 'INVALID'
            "scanned_at": datetime.utcnow(),
            "scanner": scanner_email
        }
        self.collection.insert_one(log_doc)
        return log_doc

    def get_recent_logs(self, limit=50):
        return list(self.collection.find().sort("scanned_at", DESCENDING).limit(limit))
    
    def count_invalid(self):
        return self.collection.count_documents({"action": "INVALID"})
