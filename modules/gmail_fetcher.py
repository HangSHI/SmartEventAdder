import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Updated scopes to include Gmail read access
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly'
]


def authenticate_gmail():
    """Handle OAuth 2.0 authentication flow for Gmail API."""
    creds = None

    # Check if token.json exists and load existing credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def extract_thread_id_from_url(gmail_url):
    """
    Extract thread ID from Gmail URL.

    Args:
        gmail_url (str): Full Gmail URL

    Returns:
        str: Thread ID or None if not found

    Example:
        URL: https://mail.google.com/mail/u/0/#inbox/18c8f4a2b5d6789a
        Returns: 18c8f4a2b5d6789a
    """
    import re

    # Pattern to match Gmail thread ID in URL
    # Updated to handle search URLs and longer alphanumeric IDs
    pattern = r'#(?:[^/]+/)*([a-zA-Z0-9]{16,})'
    match = re.search(pattern, gmail_url)

    if match:
        return match.group(1)

    return None


def fetch_gmail_thread_json(gmail_url):
    """
    Fetch Gmail thread JSON response directly from Gmail URL.

    Simple function that:
    1. Extracts thread ID from Gmail URL
    2. Calls Gmail threads.get() API
    3. Returns the complete JSON response for analysis

    Args:
        gmail_url (str): Gmail web interface URL

    Returns:
        dict: Raw Gmail threads.get() API JSON response

    Raises:
        Exception: If thread cannot be fetched
    """
    try:
        # Step 1: Extract thread ID from URL
        thread_id = extract_thread_id_from_url(gmail_url)
        if not thread_id:
            raise Exception(f"Could not extract thread ID from Gmail URL: {gmail_url}")

        print(f"🔍 Extracted thread ID: {thread_id}")

        # Step 2: Authenticate and build the service
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

        print(f"🔗 Calling threads.get() API with ID: {thread_id}")

        # Step 3: Call threads.get() and return raw JSON response
        thread_response = service.users().threads().get(
            userId='me',
            id=thread_id,
            format='full'
        ).execute()

        print(f"✅ API call successful! Thread contains {len(thread_response.get('messages', []))} message(s)")

        return thread_response

    except HttpError as error:
        if error.resp.status == 404:
            raise Exception(f"Thread with ID '{thread_id}' not found. Please check the Gmail URL.")
        elif error.resp.status == 403:
            raise Exception("Access denied. Please ensure Gmail API is enabled and you have proper permissions.")
        else:
            raise Exception(f"Gmail API error: {error}")
    except Exception as e:
        if "Could not extract thread ID" in str(e):
            raise e
        raise Exception(f"Failed to fetch thread from URL {gmail_url}: {str(e)}")