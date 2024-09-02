"""Module for handling Google OAuth authentication."""

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from flask import url_for
from google.oauth2.credentials import Credentials

class AuthService:
    """Service for managing Google OAuth authentication."""

    def __init__(self, config):
        """
        Initialize the AuthService.

        Args:
            config: Configuration object containing OAuth settings.
        """
        self.config = config

    def create_flow(self, state=None):
        """
        Create and return a Google OAuth2 flow.

        Args:
            state (str, optional): The state string to use for the flow.

        Returns:
            Flow: A configured Google OAuth2 flow object.
        """
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
        """
        Fetch user information using the provided Drive core object.

        Args:
            drive_core: Object containing Google Drive credentials.

        Returns:
            dict: User information from Google's OAuth2 service.
        """
        service = build('oauth2', 'v2', credentials=drive_core.credentials)
        return service.userinfo().get().execute()

    @staticmethod
    def credentials_to_dict(credentials):
        """
        Convert a Credentials object to a dictionary.

        Args:
            credentials (Credentials): Google OAuth2 credentials object.

        Returns:
            dict: Dictionary representation of the credentials.
        """
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
        """
        Convert a dictionary to a Credentials object.

        Args:
            credentials_dict (dict): Dictionary containing credential information.

        Returns:
            Credentials: Google OAuth2 credentials object.
        """
        return Credentials(**credentials_dict)