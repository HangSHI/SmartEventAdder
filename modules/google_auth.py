"""
Google OAuth2 Authentication Module

Provides unified authentication for all Google services used in SmartEventAdder:
- Gmail API (for email fetching)
- Google Calendar API (for event creation)
- Vertex AI API (for AI-powered event parsing)

This module centralizes authentication logic and provides a single source of truth
for OAuth2 credentials across all Google services.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Unified scopes for all Google services used in SmartEventAdder
SCOPES = [
    'https://www.googleapis.com/auth/calendar',        # Google Calendar API
    'https://www.googleapis.com/auth/gmail.readonly',  # Gmail API (read-only)
    'https://www.googleapis.com/auth/cloud-platform'  # Vertex AI API
]


def authenticate_google_services():
    """
    Handle OAuth 2.0 authentication flow for all Google services.

    This function provides unified authentication for Gmail, Calendar, and Vertex AI APIs.
    On first run, it will open a browser for OAuth consent. Subsequent runs will use
    stored credentials automatically.

    Returns:
        google.oauth2.credentials.Credentials: Authenticated credentials object

    Raises:
        Exception: If authentication fails or credentials.json is missing
    """
    creds = None

    # Check if token.json exists and load existing credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            creds.refresh(Request())
        else:
            # Run OAuth flow for new credentials
            if not os.path.exists('credentials.json'):
                raise Exception(
                    "credentials.json file not found. Please follow the setup instructions in README.md"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def get_authenticated_credentials():
    """
    Get authenticated Google credentials.

    Alias for authenticate_google_services() to provide a more descriptive
    function name for specific use cases.

    Returns:
        google.oauth2.credentials.Credentials: Authenticated credentials object
    """
    return authenticate_google_services()