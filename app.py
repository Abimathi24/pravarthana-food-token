import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
from flask import Flask, redirect, url_for, request, session, g
from config import Config
from firebase_config import init_firebase, auth
import functools

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Firebase
init_firebase()

# Authentication Middleware moved to utils.py to prevent circular imports

# Register Blueprint routes later to avoid circular imports
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.participants import participants_bp
from routes.scanner import scanner_bp
from routes.admin import admin_bp
from routes.public import public_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(participants_bp, url_prefix='/participants')
app.register_blueprint(scanner_bp, url_prefix='/scanner')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(public_bp)

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('scanner.index'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
