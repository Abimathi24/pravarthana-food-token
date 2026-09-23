from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from firebase_admin import auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Since Firebase Auth requires a client-side SDK for standard email/pass,
        # we will simulate it here using Custom Tokens or just verifying 
        # a token sent by the frontend Firebase JS SDK.
        
        # For simplicity in this backend-heavy setup:
        # We expect the frontend to pass an idToken via a hidden input or AJAX.
        id_token = request.form.get('idToken')
        
        if id_token:
            try:
                decoded_token = auth.verify_id_token(id_token)
                uid = decoded_token['uid']
                session['user_id'] = uid
                
                # Check email against admin list
                email = decoded_token.get('email', '')
                if email == current_app.config['ADMIN_EMAIL']:
                    session['role'] = 'admin'
                else:
                    session['role'] = 'staff'
                    
                return jsonify({"success": True, "redirect": url_for('admin.dashboard') if session['role'] == 'admin' else url_for('scanner.index')})
            except Exception as e:
                return jsonify({"error": str(e)}), 401
                
        flash('Authentication failed', 'error')
        return redirect(url_for('auth.login'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
