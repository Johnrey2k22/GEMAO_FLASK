from flask import Flask, redirect, url_for, session, render_template, g
import os
from datetime import timedelta
from MyFlaskapp.db import create_tables
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

def create_app():
    templates_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_SECURE'] = True  # Set to True for production HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or 'your-app-password'
    app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
    
    mail = Mail()
    mail.init_app(app)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    from MyFlaskapp.auth import auth_bp
    from MyFlaskapp.user import user_bp
    from MyFlaskapp.admin import admin_bp
    from MyFlaskapp.games import games_bp
    from MyFlaskapp.leaderboard import leaderboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(games_bp, url_prefix='/games')
    app.register_blueprint(leaderboard_bp, url_prefix='/leaderboard')
    
    @app.route('/')
    def index():
        return render_template('landing.html')
    
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
    
    @app.context_processor
    def inject_current_user():
        class CurrentUser:
            def __init__(self):
                self.username = session.get('user_name', 'Guest')
                self.is_authenticated = 'user_id' in session
            
        return dict(current_user=CurrentUser())
    
    return app