from flask import Blueprint, render_template, request, jsonify
from services.firebase_service import get_participants_ref
import qrcode
import base64
from io import BytesIO

public_bp = Blueprint('public', __name__)

@public_bp.route('/my-token', methods=['GET', 'POST'])
def find_token():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        college = request.form.get('college', '').strip()
        
        if not email or not name or not college:
            return render_template('public_token.html', error="Please fill in all fields.")
            
        # Search Firestore for the email
        query = get_participants_ref().where('email', '==', email).limit(1).get()
        if not query:
            return render_template('public_token.html', error="No participant found with this email address.")
            
        doc = query[0]
        data = doc.to_dict()
        
        # Verify name and college (case insensitive, loose match)
        db_name = data.get('name', '').lower()
        db_college = data.get('college', '').lower()
        
        if name.lower() not in db_name and db_name not in name.lower():
            return render_template('public_token.html', error="The Name does not match our records for this email.")
            
        if college.lower() not in db_college and db_college not in college.lower():
            return render_template('public_token.html', error="The College does not match our records for this email.")
        
        qr_token = data.get('qr_token')
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_token)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return render_template('public_token.html', participant=data, qr_b64=qr_b64)
        
    return render_template('public_token.html')

@public_bp.route('/api/status/<qr_token>')
def check_status(qr_token):
    query = get_participants_ref().where('qr_token', '==', qr_token).limit(1).get()
    if not query:
        return jsonify({"claimed": False})
    
    data = query[0].to_dict()
    return jsonify({"claimed": data.get('food_claimed', False)})
