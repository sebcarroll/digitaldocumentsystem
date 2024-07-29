from flask import Flask, session
from flask_cors import CORS
from app.routes.authorisation import auth_bp
from app.routes.access_drive import drive_bp
from app.routes.drive_operations import drive_ops_bp
from config import DevelopmentConfig, ProductionConfig
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_object(DevelopmentConfig if app.debug else ProductionConfig)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(drive_bp)
app.register_blueprint(drive_ops_bp)

# Session cleanup mechanism
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)  # Set session timeout to 30 minutes
    session.modified = True
    
    # Clean up inactive sessions
    if 'last_active' in session:
        last_active = datetime.fromtimestamp(session['last_active'])
        if datetime.now() - last_active > app.permanent_session_lifetime:
            session.clear()
    session['last_active'] = datetime.now().timestamp()

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only
    app.run(host='0.0.0.0', port=8080, debug=True)