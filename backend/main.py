"""
Main application module for the Digital Document System.

This module initializes and configures the Flask application, sets up blueprints,
Celery, and Pinecone database connections. It also includes routes for home,
Pinecone testing, and implements session management logic.
"""

from flask import Flask, session, jsonify, request, redirect, make_response
from flask_cors import CORS
from app.routes.authorisation_routes import auth_bp
from app.routes.access_drive_routes import drive_bp
from app.routes.drive_core_routes import drive_core_bp
from app.routes.drive_file_operations_routes import drive_file_ops_bp
from app.routes.drive_folder_operations_routes import drive_folder_ops_bp
from app.routes.drive_permissions_routes import drive_permissions_bp
from app.routes.drive_sharing_routes import drive_sharing_bp
from app.routes.chat_interface_routes import chat_bp
from config import DevelopmentConfig, ProductionConfig
import os
from datetime import datetime, timedelta, timezone
from app.services.database.db_service import init_db, get_db
import json
import redis

def https_redirect():
    proto = request.headers.get('X-Forwarded-Proto', 'http')
    if proto == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.before_request(https_redirect)
    allowed_origin = os.getenv('ALLOWED_ORIGIN', 'https://diganise.vercel.app')
    CORS(app, supports_credentials=True)

    app.config.from_object(ProductionConfig)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Initialize database
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
            db = get_db()
            if db is None:
                return jsonify({"error": "Failed to initialize Pinecone manager"}), 500
            if db.index is None:
                return jsonify({"error": "Pinecone index is None"}), 500
            
            stats = db.index.describe_index_stats()
            
            # Convert stats to a JSON-serializable format
            serializable_stats = json.loads(json.dumps(stats, default=str))
            
            return jsonify({
                "message": "Connected to Pinecone successfully",
                "stats": serializable_stats
            }), 200
        except Exception as e:
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
        """
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        session.modified = True
 
        user_id = session.get('user_id')
        if user_id:
            credentials_json = redis_client.get(f'user:{user_id}:token')
            if credentials_json:
                if 'last_active' in session:
                    try:
                        last_active = datetime.fromisoformat(session['last_active'])
                        # Check if user has been inactive for more than 2 minutes
                        if datetime.now(timezone.utc) - last_active > timedelta(minutes=2):
                            pass  # Add any necessary logic for inactive users
                    except ValueError:
                        pass  # Handle invalid timestamp if necessary
        
        #Set CORS headers for the preflight request
        if request.method == "OPTIONS":
         # Allows GET requests from any origin with the Content-Type
         # header and caches preflight response for an 3600s 
            headers = { "Access-Control-Allow-Origin": "https://diganise.vercel.app",
                        "Access-Control-Allow-Methods": "GET",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Credentials": "true", 
                        "Access-Control-Max-Age": "3600", }
            
            return ("", 204, headers)

        headers = {"Access-Control-Allow-Origin": "https://diganise.vercel.app",
                   "Access-Control-Allow-Credentials": "true"} 
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'https://diganise.vercel.app')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response             
    '''   
    return app

# Create the application instance
application = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port)