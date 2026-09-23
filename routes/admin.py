import os
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from firebase_config import get_db
import uuid
import datetime

admin_bp = Blueprint('admin', __name__)

# Simple dummy authentication for demo
ADMIN_PASSWORD = "password123"

@admin_bp.before_request
def check_auth():
    if request.endpoint and request.endpoint != 'admin.login' and request.endpoint != 'static':
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        return render_template('admin_login.html', error="Invalid password")
    return render_template('admin_login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

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
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                df = pd.read_excel(filepath)
            else:
                return jsonify({"error": "Unsupported file format. Please use CSV or Excel."}), 400
                
            # Expected columns: Name, Email, College (case insensitive check)
            # Map columns to standard names
            col_map = {}
            for col in df.columns:
                lower_col = str(col).lower().strip()
                if 'name' in lower_col and 'college' not in lower_col:
                    col_map[col] = 'name'
                elif 'email' in lower_col:
                    col_map[col] = 'email'
                elif 'college' in lower_col or 'institution' in lower_col:
                    col_map[col] = 'college'
            
            if not col_map:
                # Let's try to match exactly the user's provided CSV structure
                # The user's CSV has columns: StudentID,Event,SNo,TeamNo,College,Name,Phone,Email
                for col in df.columns:
                    lower_col = str(col).strip()
                    if lower_col == 'Name': col_map[col] = 'name'
                    if lower_col == 'Email': col_map[col] = 'email'
                    if lower_col == 'College': col_map[col] = 'college'
            
            df = df.rename(columns=col_map)
            
            required = ['name', 'email', 'college']
            missing = [req for req in required if req not in df.columns]
            if missing:
                return jsonify({"error": f"Missing required columns: {', '.join(missing)}"}), 400
                
            # Import to Firestore
            db = get_db()
            if not db:
                return jsonify({"error": "Database not initialized"}), 500
                
            batch = db.batch()
            collection_ref = db.collection('participants')
            
            count = 0
            for index, row in df.iterrows():
                doc_id = str(row['email']).lower().strip() if pd.notna(row['email']) else str(uuid.uuid4())
                doc_ref = collection_ref.document(doc_id)
                
                # Check if exists to not overwrite claim status if re-uploading
                doc = doc_ref.get()
                if not doc.exists:
                    batch.set(doc_ref, {
                        'name': str(row['name']).strip() if pd.notna(row['name']) else '',
                        'email': str(row['email']).lower().strip() if pd.notna(row['email']) else '',
                        'college': str(row['college']).strip() if pd.notna(row['college']) else '',
                        'status': 'NOT_CLAIMED',
                        'token_id': None,
                        'claim_time': None
                    })
                    count += 1
                
                if count % 400 == 0:  # Firestore batch limit is 500
                    batch.commit()
                    batch = db.batch()
                    
            if count % 400 != 0:
                batch.commit()
                
            return jsonify({"success": f"Imported {count} new participants successfully."})
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Unknown error"}), 500
