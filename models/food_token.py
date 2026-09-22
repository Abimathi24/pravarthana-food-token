from datetime import datetime
from pymongo import ASCENDING
import secrets

class FoodTokenModel:
    def __init__(self, db):
        self.collection = db.food_tokens
        self.collection.create_index([("qr_token", ASCENDING)], unique=True)
        self.collection.create_index([("registration_id", ASCENDING)], unique=True)

    def generate_token(self, participant_id, registration_id):
        # Generate a secure random hex token
        secure_token = f"FT-2026-{secrets.token_hex(8).upper()}"
        
        token_doc = {
            "participant_id": participant_id,
            "registration_id": registration_id,
            "qr_token": secure_token,
            "status": "NOT_CLAIMED",
            "generated_at": datetime.utcnow(),
            "claimed_at": None,
            "email_status": "PENDING"
        }
        
        self.collection.insert_one(token_doc)
        return token_doc

    def find_by_reg_id(self, reg_id):
        return self.collection.find_one({"registration_id": reg_id})

    def find_by_qr_token(self, qr_token):
        return self.collection.find_one({"qr_token": qr_token})

    def claim_token(self, qr_token):
        # Atomic update to prevent double scanning/race conditions
        result = self.collection.update_one(
            {"qr_token": qr_token, "status": "NOT_CLAIMED"},
            {
                "$set": {
                    "status": "CLAIMED",
                    "claimed_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    def get_stats(self):
        total = self.collection.count_documents({})
        claimed = self.collection.count_documents({"status": "CLAIMED"})
        not_claimed = self.collection.count_documents({"status": "NOT_CLAIMED"})
        return {
            "total": total,
            "claimed": claimed,
            "not_claimed": not_claimed
        }
