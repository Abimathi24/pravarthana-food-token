import os
import csv
import io
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from firebase_config import get_db
import uuid
import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def check_auth():
    if 'user_id' not in session or session.get('role') != 'admin':
        if request.path.startswith('/admin/api') or request.path == '/admin/upload':
            return jsonify({"error": "Unauthorized. Please log in again."}), 401
        return redirect(url_for('auth.login'))


@admin_bp.route('/')
def dashboard():
    db = get_db()
    if not db:
        return render_template('admin_dashboard.html', error="Database connection failed. Is Firebase configured?")
    
    return render_template('admin_dashboard.html')

@admin_bp.route('/api/stats', methods=['GET'])
def get_stats():
    db = get_db()
    if not db:
        return jsonify({"error": "No DB"}), 500

    participants_ref = db.collection('participants')
    all_participants = list(participants_ref.stream())
    
    total = len(all_participants)
    claimed = sum(1 for p in all_participants if p.to_dict().get('status') == 'CLAIMED')
    not_claimed = total - claimed
    
    # Get recent claims
    recent_claims = []
    for p in all_participants:
        data = p.to_dict()
        if data.get('status') == 'CLAIMED':
            recent_claims.append({
                'id': p.id,
                'name': data.get('name'),
                'email': data.get('email'),
                'college': data.get('college'),
                'claim_time': data.get('claim_time'),
                'token_id': data.get('token_id')
            })
            
    # Sort by claim time descending
    recent_claims.sort(key=lambda x: x.get('claim_time', ''), reverse=True)
    
    return jsonify({
        "total": total,
        "claimed": claimed,
        "not_claimed": not_claimed,
        "recent_claims": recent_claims
    })

@admin_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = file.filename
        
        try:
            if not (filename.endswith('.csv') or filename.endswith('.xlsx') or filename.endswith('.xls')):
                return jsonify({"error": "Unsupported file format. Please use CSV or Excel (.xlsx)."}), 400
                
            csv_input = []
            
            if filename.endswith('.csv'):
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_reader = csv.reader(stream)
                try:
                    headers = next(csv_reader)
                    csv_input = list(csv_reader)
                except StopIteration:
                    return jsonify({"error": "Empty CSV file."}), 400
            else:
                import openpyxl
                # Process Excel file using openpyxl (data_only to get values, read_only for memory efficiency)
                workbook = openpyxl.load_workbook(file.stream, data_only=True, read_only=True)
                sheet = workbook.active
                
                rows = list(sheet.iter_rows(values_only=True))
                if not rows:
                    return jsonify({"error": "Empty Excel file."}), 400
                    
                headers = [str(cell) if cell is not None else "" for cell in rows[0]]
                csv_input = []
                for row in rows[1:]:
                    # Skip completely empty rows
                    if any(cell is not None and str(cell).strip() != "" for cell in row):
                        csv_input.append([str(cell).strip() if cell is not None else "" for cell in row])
                
            headers_lower = [str(h).lower().strip() for h in headers]
            
            col_map = {}
            # First pass: exact match
            for i, col in enumerate(headers_lower):
                if col == 'name' and 'name' not in col_map.values():
                    col_map[i] = 'name'
                elif col == 'email' and 'email' not in col_map.values():
                    col_map[i] = 'email'
                elif col in ['college', 'institution'] and 'college' not in col_map.values():
                    col_map[i] = 'college'
                    
            # Second pass: partial match
            for i, col in enumerate(headers_lower):
                if 'name' in col and 'college' not in col and 'name' not in col_map.values():
                    col_map[i] = 'name'
                elif 'email' in col and 'email' not in col_map.values():
                    col_map[i] = 'email'
                elif ('college' in col or 'institution' in col) and 'college' not in col_map.values():
                    col_map[i] = 'college'
                    
            required = ['name', 'email', 'college']
            missing = [req for req in required if req not in col_map.values()]
            if missing:
                return jsonify({"error": f"Missing required columns: {', '.join(missing)}"}), 400
                
            db = get_db()
            if not db:
                return jsonify({"error": "Database not initialized"}), 500
                
            batch = db.batch()
            collection_ref = db.collection('participants')
            
            count = 0
            for row in csv_input:
                row_data = {}
                for i, val in enumerate(row):
                    if i in col_map:
                        row_data[col_map[i]] = val.strip() if val else ''
                        
                email = row_data.get('email', '').lower()
                name = row_data.get('name', '')
                college = row_data.get('college', '')
                
                doc_id = email if email else str(uuid.uuid4())
                doc_ref = collection_ref.document(doc_id)
                
                doc = doc_ref.get()
                if not doc.exists:
                    batch.set(doc_ref, {
                        'name': name,
                        'email': email,
                        'college': college,
                        'status': 'NOT_CLAIMED',
                        'token_id': None,
                        'claim_time': None
                    })
                    count += 1
                
                if count > 0 and count % 400 == 0:
                    batch.commit()
                    batch = db.batch()
                    
            if count % 400 != 0:
                batch.commit()
                
            return jsonify({"success": f"Imported {count} new participants successfully."})
            
        except UnicodeDecodeError:
            return jsonify({"error": "Failed to read file. Please ensure it is saved with UTF-8 encoding."}), 400
        except Exception as e:
            import traceback
            return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 400
            
    return jsonify({"error": "Unknown error"}), 400

@admin_bp.route('/api/add_participant', methods=['POST'])
def add_participant():
    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
        
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').lower().strip()
    college = data.get('college', '').strip()
    
    if not name or not college:
        return jsonify({"error": "Name and College are required."}), 400
        
    doc_id = email if email else str(uuid.uuid4())
    doc_ref = db.collection('participants').document(doc_id)
    
    # Check if exists
    if doc_ref.get().exists and email:
        return jsonify({"error": "A participant with this email is already registered."}), 400
        
    doc_ref.set({
        'name': name,
        'email': email,
        'college': college,
        'status': 'NOT_CLAIMED',
        'token_id': None,
        'claim_time': None
    })
    
    return jsonify({"success": f"Participant {name} added successfully."})

@admin_bp.route('/api/wipe_database', methods=['DELETE'])
def wipe_database():
    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        # Delete all participants
        participants = db.collection('participants').stream()
        for doc in participants:
            doc.reference.delete()
            
        # Delete all food_claims logs if they exist
        claims = db.collection('food_claims').stream()
        for doc in claims:
            doc.reference.delete()
            
        return jsonify({"success": "Database wiped successfully. All participants have been deleted."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/undo_claim/<participant_id>', methods=['POST'])
def undo_claim(participant_id):
    db = get_db()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        doc_ref = db.collection('participants').document(participant_id)
        if not doc_ref.get().exists:
            return jsonify({"error": "Participant not found."}), 404
            
        doc_ref.update({
            'status': 'NOT_CLAIMED',
            'token_id': None,
            'claim_time': None
        })
        return jsonify({"success": "Claim removed successfully. Participant is still registered."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
