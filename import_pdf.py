import re
import os
from config import Config
from pymongo import MongoClient
import uuid
from datetime import datetime

# Initialize DB
client = MongoClient(Config.MONGO_URI)
db = client[Config.MONGO_DB_NAME]
collection = db.participants

def parse_and_insert():
    with open('participants_valid.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    email_pattern = re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
    
    total_inserted = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Basic heuristic: The first few words are the college
        parts = line.split()
        college = "Unknown"
        if len(parts) > 3:
            college = " ".join(parts[:3])
            
        # Find all emails in the line
        emails = email_pattern.findall(line)
        
        for email in emails:
            # We don't have a clean way to extract names from this messy OCR without complex NLP.
            # We'll use the part of the email before the @ as a placeholder name
            name_placeholder = email.split('@')[0]
            
            # Use email as unique identifier for registration_id for this import
            reg_id = "REG-" + str(uuid.uuid4())[:6].upper()
            
            doc = {
                "registration_id": reg_id,
                "name": name_placeholder,
                "email": email,
                "phone": "Imported",
                "college": college,
                "department": "Imported",
                "event": "Imported",
                "created_at": datetime.utcnow()
            }
            
            try:
                collection.insert_one(doc)
                total_inserted += 1
            except Exception as e:
                # Might fail if email already exists due to unique index
                pass
                
    print(f"Successfully inserted {total_inserted} participants.")

if __name__ == "__main__":
    parse_and_insert()
