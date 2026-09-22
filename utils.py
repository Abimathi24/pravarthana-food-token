import functools
from flask import session, redirect, url_for, request, g
from firebase_config import auth

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        try:
            user = auth.get_user(session['user_id'])
            g.user = user
            g.role = session.get('role', 'staff')
        except Exception:
            session.clear()
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return "Admin Access Required", 403
        return f(*args, **kwargs)
    return decorated_function
