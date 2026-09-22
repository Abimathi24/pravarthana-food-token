from flask import Blueprint, render_template, jsonify
from utils import login_required, admin_required
from services.firebase_service import get_dashboard_stats

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
@admin_required
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/stats')
@login_required
@admin_required
def get_stats():
    stats = get_dashboard_stats()
    return jsonify(stats)
