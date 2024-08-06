from flask import Flask, session, jsonify
from flask_cors import CORS
from app.routes.authorisation import auth_bp
from app.routes.access_drive import drive_bp
from app.routes.drive_core import drive_core_bp
from app.routes.drive_file_operations import drive_file_ops_bp
from app.routes.drive_folder_operations import drive_folder_ops_bp
from app.routes.drive_permissions import drive_permissions_bp
from app.routes.drive_sharing import drive_sharing_bp
from config import DevelopmentConfig, ProductionConfig
from database.pinecone_manager import PineconeManager
import os
from datetime import datetime, timedelta
from database.db import init_db, get_db


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(DevelopmentConfig if app.debug else ProductionConfig)

    # Initialize Pinecone
    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(drive_bp)
    app.register_blueprint(drive_core_bp)
    app.register_blueprint(drive_file_ops_bp)
    app.register_blueprint(drive_folder_ops_bp)
    app.register_blueprint(drive_permissions_bp)
    app.register_blueprint(drive_sharing_bp)

    @app.route('/test_pinecone')
    def test_pinecone():
        try:
            stats = get_db().index.describe_index_stats()
            return jsonify({
                "message": "Connected to Pinecone successfully",
                "stats": stats
            }), 200
        except Exception as e:
            return jsonify({
                "error": str(e)
            }), 500

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        session.modified = True
        
        if 'last_active' in session:
            last_active = datetime.fromtimestamp(session['last_active'])
            if datetime.now() - last_active > app.permanent_session_lifetime:
                session.clear()
        session['last_active'] = datetime.now().timestamp()

    return app

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)