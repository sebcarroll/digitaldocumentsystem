from flask import Flask, session, jsonify
from flask_cors import CORS
from app.routes.authorisation import auth_bp
from app.routes.access_drive import drive_bp
from app.routes.drive_core import drive_core_bp
from app.routes.drive_file_operations import drive_file_ops_bp
from app.routes.drive_folder_operations import drive_folder_ops_bp
from app.routes.drive_permissions import drive_permissions_bp
from app.routes.drive_sharing import drive_sharing_bp
from app.routes.sync_routes import sync_bp
from celery_app import init_celery
from celery_app import celery_app
from config import DevelopmentConfig, ProductionConfig
import os
from datetime import datetime, timedelta
from app.services.database.db import init_db, get_db
from app.services.sync.sync_service import SyncService
import json
import logging

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #For Development purposes only
    CORS(app, supports_credentials=True)
    app.config.from_object(DevelopmentConfig if app.debug else ProductionConfig)

    # Initialize Celery
    init_celery(app)

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
    app.register_blueprint(sync_bp)

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
        
        if 'credentials' in session and 'user_id' in session:
            logger.info(f"Session contains credentials and user_id")
            if 'last_active' in session:
                last_active = datetime.fromtimestamp(session['last_active'])
                if datetime.now() - last_active > timedelta(minutes=2):
                    logger.info("Initiating sync due to inactivity")
                    try:
                        result = SyncService.sync_user_drive(session)
                        logger.info(f"Sync result: {result}")
                    except Exception as e:
                        logger.exception(f"Error during sync: {str(e)}")
                else:
                    logger.info("Skipping sync due to recent activity")
            else:
                logger.warning("No last_active timestamp in session")
        else:
            logger.warning("Missing credentials or user_id in session")
        
        session['last_active'] = datetime.now().timestamp()
        
    return app

# Create the application instance
application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080, ssl_context='adhoc', debug=True)
