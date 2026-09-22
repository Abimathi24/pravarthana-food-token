from flask import Blueprint, render_template, request, jsonify
from utils import login_required, admin_required
from services.firebase_service import get_participants_ref, add_participant

participants_bp = Blueprint('participants', __name__)

@participants_bp.route('/')
@login_required
@admin_required
def index():
    return render_template('participants.html')

@participants_bp.route('/api/list')
@login_required
@admin_required
def list_participants():
    docs = get_participants_ref().order_by('created_at', direction='DESCENDING').limit(100).stream()
    participants = []
    for doc in docs:
        data = doc.to_dict()
        data['_id'] = doc.id
        # Convert DatetimeWithNanoseconds to string if needed
        if 'created_at' in data and data['created_at']:
            data['created_at'] = str(data['created_at'])
        participants.append(data)
    return jsonify(participants)

@participants_bp.route('/api/add', methods=['POST'])
@login_required
@admin_required
def add_participant_route():
    data = request.json
    try:
        add_participant(data)
        return jsonify({"message": "Participant added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
