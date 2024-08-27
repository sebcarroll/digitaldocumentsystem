"""
Main application module for the Google Drive Sync API.

This module initializes and configures the Flask application, sets up blueprints,
Celery, and Pinecone database connections. It also includes routes for home,
Pinecone testing, and implements session management logic.
"""

from flask import Flask, session, jsonify
from flask_cors import CORS
from app.routes.authorisation_routes import auth_bp
from app.routes.access_drive_routes import drive_bp
from app.routes.drive_core_routes import drive_core_bp
from app.routes.drive_file_operations_routes import drive_file_ops_bp
from app.routes.drive_folder_operations_routes import drive_folder_ops_bp
from app.routes.drive_permissions_routes import drive_permissions_bp
from app.routes.drive_sharing_routes import drive_sharing_bp
from app.routes.chat_interface_routes import chat_bp
# from celery_app import init_celery
# from celery_app import celery_app
from config import DevelopmentConfig, ProductionConfig
import os
from datetime import datetime, timedelta, timezone
from app.services.database.db_service import init_db, get_db
# from app.services.sync.sync_service import SyncService
import json
import logging
import redis

logger = logging.getLogger(__name__)

def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For Development purposes only
    CORS(app, supports_credentials=True)
    app.config.from_object(DevelopmentConfig if app.debug else ProductionConfig)

    # Initialize Celery
#   init_celery(app)

    # Initialize Pinecone
    init_db(app)

    # Initialize Redis client
    redis_client = redis.StrictRedis.from_url(app.config['REDIS_TOKEN_URL'], decode_responses=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(drive_bp)
    app.register_blueprint(drive_core_bp)
    app.register_blueprint(drive_file_ops_bp)
    app.register_blueprint(drive_folder_ops_bp)
    app.register_blueprint(drive_permissions_bp)
    app.register_blueprint(drive_sharing_bp)
    app.register_blueprint(chat_bp, url_prefix='/chat')

    @app.route('/')
    def home():
        """
        Handle requests to the home route.

        Returns:
            str: A welcome message.
        """
        return "Welcome to the backend API"

    @app.route('/test_pinecone')
    def test_pinecone():
        """
        Test the Pinecone connection and retrieve index statistics.

        Returns:
            flask.Response: A JSON response with Pinecone connection status and stats.
        """
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
        """
        Perform actions before each request is processed.

        This function manages session lifetime and checks user authentication.
        It performs the following tasks:
        1. Sets the session to be permanent and updates its lifetime.
        2. Checks for user authentication by verifying the presence of user_id in the session.
        3. Verifies the presence of user credentials in Redis.
        4. Updates the last active timestamp for the current request.

        The function uses Redis to store and retrieve user credentials, and logs various
        steps and potential issues for debugging purposes.
        """
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        session.modified = True
        
        user_id = session.get('user_id')
        if user_id:
            logger.info(f"Session contains user_id: {user_id}")
            credentials_json = redis_client.get(f'user:{user_id}:token')
            if credentials_json:
                logger.info(f"Credentials found in Redis for user {user_id}")
                if 'last_active' in session:
                    try:
                        last_active = datetime.fromisoformat(session['last_active'])
                        if datetime.now(timezone.utc) - last_active > timedelta(minutes=2):
                            logger.info("User inactive for more than 2 minutes")
                        else:
                            logger.info("User active within last 2 minutes")
                    except ValueError:
                        logger.warning("Invalid last_active timestamp in session")
                else:
                    logger.warning("No last_active timestamp in session")
            else:
                logger.warning(f"No credentials found in Redis for user {user_id}")
        else:
            logger.warning("No user_id in session")
        
        # Update the last active timestamp
        session['last_active'] = datetime.now(timezone.utc).isoformat()
        
    return app

# Create the application instance
application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080, ssl_context='adhoc', debug=True)