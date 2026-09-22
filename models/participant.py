import uuid
from datetime import datetime
from pymongo import ASCENDING

class ParticipantModel:
    def __init__(self, db):
        self.collection = db.participants
        self.collection.create_index([("registration_id", ASCENDING)], unique=True)
        self.collection.create_index([("email", ASCENDING)], unique=True)

    def create(self, data):
        participant = {
            "registration_id": data.get("registration_id", str(uuid.uuid4())[:8]),
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "college": data.get("college"),
            "department": data.get("department"),
            "event": data.get("event"),
            "created_at": datetime.utcnow()
        }
        result = self.collection.insert_one(participant)
        return participant

    def find_all(self, filter_query=None):
        if filter_query is None:
            filter_query = {}
        return list(self.collection.find(filter_query).sort("created_at", -1))

    def find_by_reg_id(self, reg_id):
        return self.collection.find_one({"registration_id": reg_id})
    
    def count(self):
        return self.collection.count_documents({})
