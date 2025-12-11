from flask import Flask, redirect, url_for, session
import os
from datetime import timedelta
from MyFlaskapp.db import create_user_table

def create_app():
    templates_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    from MyFlaskapp.auth import auth_bp
    from MyFlaskapp.user import user_bp
    from MyFlaskapp.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    @app.route('/favicon.ico')
    def favicon():
        from flask import send_from_directory
        import os
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                  'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    @app.route('/debug/session')
    def debug_session():
        from flask import jsonify
        return jsonify({
            'session_data': dict(session),
            'is_logged_in': 'user_id' in session,
            'user_info': {
                'user_id': session.get('user_id'),
                'user_name': session.get('user_name'),
                'user_role': session.get('user_role')
            } if 'user_id' in session else None
        })
    
    create_user_table()
    return app
