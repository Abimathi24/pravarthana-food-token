from flask import Blueprint, render_template, request, jsonify, url_for
from firebase_config import get_db
import datetime
import qrcode
import io
import base64

public_bp = Blueprint('public', __name__)

@public_bp.route('/claim')
def claim_page():
    return render_template('claim.html')

@public_bp.route('/api/claim', methods=['POST'])
def process_claim():
    data = request.json
    name = data.get('name', '').strip().lower()
    email = data.get('email', '').strip().lower()
    college = data.get('college', '').strip().lower()
    
    if not name and not email and not college:
        return jsonify({"status": "error", "message": "Please enter Name, Email or College Name to search."}), 400
        
    db = get_db()
    if not db:
        return jsonify({"status": "error", "message": "Database error."}), 500
        
    participants_ref = db.collection('participants')
    
    # Simple search strategy:
    # First try exact match on email, as it's a unique identifier
    matched_doc = None
    
    if email:
        docs = participants_ref.where('email', '==', email).limit(1).stream()
        for doc in docs:
            matched_doc = doc
            break
            
    # If no email match, try name
    if not matched_doc and name:
        docs = participants_ref.where('name', '==', data.get('name', '').strip()).limit(1).stream()
        for doc in docs:
            matched_doc = doc
            break
            
    # If still no match and college is provided
    # Note: Querying by college might return many results. We'll just take the first match.
    # In a real scenario, this might need refinement.
    if not matched_doc and college:
        docs = participants_ref.where('college', '==', data.get('college', '').strip()).limit(1).stream()
        for doc in docs:
            matched_doc = doc
            break
            
    if not matched_doc:
        return jsonify({
            "status": "not_found",
            "message": "Only Pravarthana26 registered participants can claim a food token."
        })
        
    participant = matched_doc.to_dict()
    
    if participant.get('status') == 'CLAIMED':
        return jsonify({
            "status": "already_claimed",
            "message": "This participant has already received the Pravarthana26 food token."
        })
        
    # Generate Token ID
    token_id = f"P26-FT-{str(matched_doc.id)[:5].upper()}-{datetime.datetime.now().strftime('%M%S')}"
    claim_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update Document
    matched_doc.reference.update({
        'status': 'CLAIMED',
        'token_id': token_id,
        'claim_time': claim_time
    })
    
    return jsonify({
        "status": "success",
        "data": {
            "name": participant.get('name', 'Unknown'),
            "college": participant.get('college', 'Unknown'),
            "token_id": token_id,
            "status": "CLAIMED"
        }
    })

@public_bp.route('/qr')
def generate_qr():
    # URL to the claim page
    claim_url = request.host_url.rstrip('/') + url_for('public.claim_page')
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(claim_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_b64 = base64.b64encode(img_io.getvalue()).decode()
    
    return f'''
    <html>
        <head>
            <title>QR Code</title>
            <style>
                body {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; background: #f8f9fa; }}
                img {{ max-width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                h2 {{ color: #333; }}
            </style>
        </head>
        <body>
            <h2>Pravarthana26 Food Token QR</h2>
            <img src="data:image/png;base64,{img_b64}" alt="QR Code">
            <p>Scan to open claim form</p>
        </body>
    </html>
    '''
