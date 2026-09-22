from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils import admin_required, login_required
from services.firebase_service import get_participants_ref
from services.pdf_import_service import process_pdf_import
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_pdf():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['pdf_file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        # Save temp file
        temp_path = os.path.join('scratch', file.filename)
        os.makedirs('scratch', exist_ok=True)
        file.save(temp_path)
        
        # Process
        result = process_pdf_import(temp_path)
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if "error" in result:
            return jsonify(result), 500
            
        return jsonify(result)
        
    return render_template('import.html')

@admin_bp.route('/wipe', methods=['POST'])
@login_required
@admin_required
def wipe_participants():
    try:
        # In firestore, deleting a collection requires fetching all documents and deleting them one by one
        # or in batches. For ~240 docs, we can do it iteratively.
        docs = get_participants_ref().stream()
        deleted = 0
        for doc in docs:
            doc.reference.delete()
            deleted += 1
        return jsonify({"success": True, "deleted": deleted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
