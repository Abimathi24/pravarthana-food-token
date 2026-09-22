from flask import Blueprint, render_template, request, jsonify, g
from utils import login_required
from services.firebase_service import process_qr_scan

scanner_bp = Blueprint('scanner', __name__)

@scanner_bp.route('/')
@login_required
def index():
    return render_template('scanner.html')

@scanner_bp.route('/api/scan', methods=['POST'])
@login_required
def scan_qr():
    data = request.json
    qr_token = data.get('qr_token')
    
    if not qr_token:
        return jsonify({"status": "INVALID", "message": "No QR token provided."}), 400
        
    # Process scan transactionally
    result = process_qr_scan(qr_token, g.user.email)
    
    status_code = 200 if result['status'] == 'SUCCESS' else 400
    if result['status'] == 'INVALID':
        status_code = 404
        
    return jsonify(result), status_code
