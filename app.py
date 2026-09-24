import os
from flask import Flask, redirect, url_for, jsonify

from config import Config

# Initialize app
app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'pravarthana26_super_secret_key')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Firebase
from firebase_config import init_firebase
init_firebase()

# Import routes
from routes.admin import admin_bp
from routes.public import public_bp
from routes.auth import auth_bp
from routes.scanner import scanner_bp

# Register blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(public_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(scanner_bp, url_prefix='/scanner')

@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if hasattr(e, 'code'):
        return jsonify(error=str(e)), e.code
    import traceback
    return jsonify({"error": "Unhandled Exception", "traceback": traceback.format_exc()}), 500

@app.route('/')
def index():
    # Redirect root to claim page or admin dashboard depending on requirement
    return redirect(url_for('public.claim_page'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
