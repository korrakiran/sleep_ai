"""
Sleep Paralysis AI - Flask Application Factory (MongoDB Version)
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .models.database import init_db
from .routes.auth import auth_bp
from .routes.tracker import tracker_bp
from .routes.prediction import prediction_bp
from .routes.alarm import alarm_bp
from .routes.insights import insights_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────────────
    # Fallback secrets since they are removed from .env
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sleep-paralysis-default-secret-key-123')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'sleep-paralysis-jwt-default-secret-456')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

    # ── Extensions ─────────────────────────────────────────────────────────────
    CORS(app, origins="*", supports_credentials=True)
    JWTManager(app)

    # ── Register Blueprints ────────────────────────────────────────────────────
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tracker_bp, url_prefix='/api/tracker')
    app.register_blueprint(prediction_bp, url_prefix='/api/predict')
    app.register_blueprint(alarm_bp, url_prefix='/api/alarm')
    app.register_blueprint(insights_bp, url_prefix='/api/insights')

    # ── Database Init ──────────────────────────────────────────────────────────
    init_db()

    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Sleep Paralysis AI (Sarvam AI)', 'version': '1.1.0'}

    return app
