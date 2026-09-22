from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from models.food_token import FoodTokenModel
from models.participant import ParticipantModel
from services.qr_service import QRService
import app as main_app

tokens_bp = Blueprint('tokens', __name__)

@tokens_bp.route('/')
@login_required
def index():
    return render_template('tokens.html')

@tokens_bp.route('/api/generate', methods=['POST'])
@login_required
def generate_token():
    data = request.json
    registration_id = data.get('registration_id')
    
    if not registration_id:
        return jsonify({"error": "Registration ID required"}), 400
        
    participant_model = ParticipantModel(main_app.db)
    token_model = FoodTokenModel(main_app.db)
    
    participant = participant_model.find_by_reg_id(registration_id)
    if not participant:
        return jsonify({"error": "Participant not found"}), 404
        
    # Check if token already exists
    if token_model.find_by_reg_id(registration_id):
        return jsonify({"error": "Token already exists for this participant"}), 400
        
    # Generate Token
    try:
        token = token_model.generate_token(str(participant['_id']), registration_id)
        # Generate QR Base64
        qr_base64 = QRService.generate_qr_base64(token['qr_token'])
        
        return jsonify({
            "message": "Token generated successfully",
            "token": token['qr_token'],
            "qr_image": qr_base64
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
