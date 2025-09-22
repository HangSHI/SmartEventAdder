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
import google.auth
from google.auth import default

# Unified scopes for all Google services used in SmartEventAdder
SCOPES = [
    'https://www.googleapis.com/auth/calendar',        # Google Calendar API
    'https://www.googleapis.com/auth/gmail.readonly',  # Gmail API (read-only)
    'https://www.googleapis.com/auth/cloud-platform'  # Vertex AI API
]


def authenticate_google_services():
    """
    Handle authentication for all Google services with support for both
    local development (OAuth2) and production deployment (Application Default Credentials).

    This function provides unified authentication for Gmail, Calendar, and Vertex AI APIs.

    - In production (Google Cloud Run): Uses Application Default Credentials (ADC)
    - In development: Uses OAuth2 flow with credentials.json/token.json

    Returns:
        google.auth.credentials.Credentials: Authenticated credentials object

    Raises:
        Exception: If authentication fails
    """
    # Check if we're running in a production environment (Google Cloud)
    environment = os.getenv('ENVIRONMENT', 'development').lower()
    is_production = environment in ['production', 'prod']

    # Also check for Google Cloud environment variables
    is_google_cloud = (
        os.getenv('GOOGLE_CLOUD_PROJECT') or
        os.getenv('GOOGLE_CLOUD_PROJECT_ID') or
        os.getenv('K_SERVICE')  # Cloud Run service name env var
    )

    if is_production or is_google_cloud:
        # Production: Use Application Default Credentials
        try:
            print("Using Application Default Credentials for production environment")
            creds, project = default(scopes=SCOPES)

            # Ensure credentials are valid
            if not creds.valid:
                creds.refresh(Request())

            print(f"Successfully authenticated with ADC for project: {project}")
            return creds

        except Exception as e:
            print(f"ADC authentication failed: {str(e)}")
            raise Exception(
                f"Production authentication failed. Ensure the service account has the required permissions. Error: {str(e)}"
            )

    else:
        # Development: Use OAuth2 flow with local files
        print("Using OAuth2 flow for development environment")
        creds = None

        # Check if token.json exists and load existing credentials
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired credentials
                print("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                # Run OAuth flow for new credentials
                if not os.path.exists('credentials.json'):
                    raise Exception(
                        "credentials.json file not found. Please follow the setup instructions in README.md"
                    )

                print("Starting OAuth2 authentication flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                print("Credentials saved to token.json")

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