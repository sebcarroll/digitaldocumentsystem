from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from flask import url_for
from google.oauth2.credentials import Credentials

class AuthService:
    def __init__(self, config):
        self.config = config

    def create_flow(self, state=None):
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.config.GOOGLE_CLIENT_ID,
                    "client_secret": self.config.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": [self.config.GOOGLE_REDIRECT_URI]
                }
            },
            scopes=self.config.SCOPES,
            state=state,
            redirect_uri=url_for('auth.oauth2callback', _external=True)
        )
        return flow

    @staticmethod
    def fetch_user_info(drive_core):
        service = build('oauth2', 'v2', credentials=drive_core.credentials)
        return service.userinfo().get().execute()

    @staticmethod
    def credentials_to_dict(credentials):
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

    @staticmethod
    def dict_to_credentials(credentials_dict):
        return Credentials(**credentials_dict)