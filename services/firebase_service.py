from firebase_config import get_db
from firebase_admin import firestore
import datetime
import secrets

def get_participants_ref():
    return get_db().collection('participants')

def get_claims_ref():
    return get_db().collection('food_claims')

def add_participant(data):
    # Ensure participant_id is unique by using it as document ID, or checking.
    # We will use the provided participant_id as the Document ID
    pid = data.get('participant_id')
    doc_ref = get_participants_ref().document(pid)
    
    # Generate unique QR token
    qr_token = f"PRAVARTHANA26-{pid}-{secrets.token_hex(4).upper()}"
    
    doc_data = {
        'participant_id': pid,
        'name': data.get('name'),
        'email': data.get('email', ''),
        'phone': data.get('phone', ''),
        'college': data.get('college', ''),
        'department': data.get('department', ''),
        'event': data.get('event', ''),
        'qr_token': qr_token,
        'food_claimed': False,
        'claim_date': None,
        'claim_time': None,
        'claimed_by': None,
        'created_at': firestore.SERVER_TIMESTAMP
    }
    
    doc_ref.set(doc_data)
    return doc_data

@firestore.transactional
def claim_food_transaction(transaction, participant_ref, staff_email):
    snapshot = participant_ref.get(transaction=transaction)
    
    if not snapshot.exists:
        return {"status": "INVALID", "message": "Participant not found."}
        
    data = snapshot.to_dict()
    
    if data.get('food_claimed') is True:
        return {
            "status": "ALREADY_CLAIMED", 
            "message": "Food already claimed.",
            "name": data.get('name'),
            "participant_id": data.get('participant_id'),
            "previous_claim_date": data.get('claim_date'),
            "previous_claim_time": data.get('claim_time'),
            "claimed_by": data.get('claimed_by')
        }
        
    # Claim it
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    transaction.update(participant_ref, {
        'food_claimed': True,
        'claim_date': date_str,
        'claim_time': time_str,
        'claimed_by': staff_email
    })
    
    # We must return the success data to create the log later
    return {
        "status": "SUCCESS",
        "participant_id": data.get('participant_id'),
        "qr_token": data.get('qr_token'),
        "name": data.get('name'),
        "college": data.get('college'),
        "event": data.get('event'),
        "date": date_str,
        "time": time_str
    }

def process_qr_scan(qr_token, staff_email):
    # Find participant by qr_token
    # Firestore doesn't allow transactional queries on non-document paths easily.
    # So we query first, then run transaction on the specific doc.
    query = get_participants_ref().where('qr_token', '==', qr_token).limit(1).get()
    
    if not query:
        return {"status": "INVALID", "message": "Invalid QR code."}
        
    doc = query[0]
    participant_ref = doc.reference
    
    transaction = get_db().transaction()
    result = claim_food_transaction(transaction, participant_ref, staff_email)
    
    if result['status'] == 'SUCCESS':
        # Create log entry
        claim_log = {
            'participant_id': result['participant_id'],
            'qr_token': result['qr_token'],
            'participant_name': result['name'],
            'college': result['college'],
            'event': result['event'],
            'claimed_at': firestore.SERVER_TIMESTAMP,
            'claimed_by': staff_email,
            'status': 'APPROVED'
        }
        get_claims_ref().add(claim_log)
        
    return result

def get_dashboard_stats():
    # In a real large-scale app, use aggregation queries. 
    # For a symposium size (thousands), client-side counting is okay.
    participants = get_participants_ref().get()
    
    total = 0
    claimed = 0
    
    for p in participants:
        total += 1
        data = p.to_dict()
        if data.get('food_claimed') is True:
            claimed += 1
            
    return {
        "total": total,
        "claimed": claimed,
        "unclaimed": total - claimed,
        "percentage": round((claimed / total * 100), 1) if total > 0 else 0
    }
