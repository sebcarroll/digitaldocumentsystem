from flask import Flask
from flask_cors import CORS
from app.routes.authorisation import auth_bp
from app.routes.access_drive import drive_bp
from config import DevelopmentConfig, ProductionConfig
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_object(DevelopmentConfig if app.debug else ProductionConfig)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(drive_bp)

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only
    app.run(host='0.0.0.0', port=8080, debug=True)