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
import os
from datetime import datetime, timedelta
from app.services.database.db import init_db, get_db
import json
import logging

logger = logging.getLogger(__name__)

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

    @app.route('/')
    def home():
        return "Welcome to the backend API"

    @app.route('/test_pinecone')
    def test_pinecone():
        try:
            logger.info("Entering test_pinecone function")
            db = get_db()
            logger.info(f"DB object: {db}")
            if db is None:
                logger.error("Pinecone manager is None")
                return jsonify({"error": "Failed to initialize Pinecone manager"}), 500
            logger.info(f"DB index: {db.index}")
            if db.index is None:
                logger.error("Pinecone index is None")
                return jsonify({"error": "Pinecone index is None"}), 500
            logger.info("Calling describe_index_stats")
            stats = db.index.describe_index_stats()
            logger.info(f"Stats: {stats}")
            
            # Convert stats to a JSON-serializable format
            serializable_stats = json.loads(json.dumps(stats, default=str))
            
            return jsonify({
                "message": "Connected to Pinecone successfully",
                "stats": serializable_stats
            }), 200
        except Exception as e:
            logger.error(f"Error in test_pinecone: {str(e)}", exc_info=True)
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

# Create the application instance
application = create_app()

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only
    application.run(host='0.0.0.0', port=8080, debug=True)