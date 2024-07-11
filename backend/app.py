from flask import Flask
from routes.authorisation import auth_bp
from routes.access_drive import drive_bp
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(drive_bp)

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only
    app.run('localhost', 8080, debug=True)