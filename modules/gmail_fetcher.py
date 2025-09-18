import base64
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


def fetch_email_by_id(message_id):
    """
    Fetch email content by Gmail message ID.

    Args:
        message_id (str): Gmail message ID (e.g., "18c8f4a2b5d6789a")

    Returns:
        str: Email content including subject and body

    Raises:
        Exception: If email cannot be fetched or doesn't exist
    """
    try:
        # Authenticate and build the service
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

        # Get the message
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        # Extract email content
        email_content = extract_email_content(message)

        return email_content

    except HttpError as error:
        if error.resp.status == 404:
            raise Exception(f"Email with ID '{message_id}' not found. Please check the message ID.")
        elif error.resp.status == 403:
            raise Exception("Access denied. Please ensure Gmail API is enabled and you have proper permissions.")
        else:
            raise Exception(f"Gmail API error: {error}")

    except Exception as error:
        raise Exception(f"Failed to fetch email: {str(error)}")


def extract_email_content(message):
    """
    Extract readable content from Gmail message object.

    Args:
        message (dict): Gmail API message object

    Returns:
        str: Formatted email content with subject and body
    """
    # Get headers
    headers = message['payload'].get('headers', [])
    subject = ""
    sender = ""
    date = ""

    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')

        if name == 'subject':
            subject = value
        elif name == 'from':
            sender = value
        elif name == 'date':
            date = value

    # Get email body
    body = extract_message_body(message['payload'])

    # Format the email content
    email_content = f"Subject: {subject}\n"
    if sender:
        email_content += f"From: {sender}\n"
    if date:
        email_content += f"Date: {date}\n"
    email_content += f"\n{body}"

    return email_content


def extract_message_body(payload):
    """
    Extract text body from email payload, handling various MIME types.

    Args:
        payload (dict): Gmail message payload

    Returns:
        str: Email body text
    """
    body = ""

    # Check if payload has parts (multipart message)
    if 'parts' in payload:
        for part in payload['parts']:
            # Recursively extract from parts
            body += extract_message_body(part)
    else:
        # Single part message
        mime_type = payload.get('mimeType', '')

        if mime_type == 'text/plain' or mime_type == 'text/html':
            data = payload.get('body', {}).get('data', '')
            if data:
                # Decode base64url encoded data
                try:
                    decoded_bytes = base64.urlsafe_b64decode(data + '==')
                    decoded_text = decoded_bytes.decode('utf-8')

                    # If HTML, strip basic tags (simple approach)
                    if mime_type == 'text/html':
                        decoded_text = strip_html_tags(decoded_text)

                    body += decoded_text
                except Exception:
                    # If decoding fails, skip this part
                    pass

    return body


def strip_html_tags(html_text):
    """
    Simple HTML tag removal for email content.

    Args:
        html_text (str): HTML content

    Returns:
        str: Plain text content
    """
    import re

    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', html_text)

    # Replace common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')

    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()


def validate_message_id(message_id):
    """
    Validate Gmail message ID format.

    Args:
        message_id (str): Message ID to validate

    Returns:
        bool: True if valid format
    """
    import re

    # Gmail message IDs are typically 16+ character hex strings
    pattern = r'^[a-fA-F0-9]{10,}$'
    return bool(re.match(pattern, message_id))


def extract_message_id_from_url(gmail_url):
    """
    Extract message ID from Gmail URL.

    Args:
        gmail_url (str): Full Gmail URL

    Returns:
        str: Message ID or None if not found

    Example:
        URL: https://mail.google.com/mail/u/0/#inbox/18c8f4a2b5d6789a
        Returns: 18c8f4a2b5d6789a
    """
    import re

    # Pattern to match Gmail message ID in URL
    pattern = r'#[^/]*/([a-fA-F0-9]{10,})'
    match = re.search(pattern, gmail_url)

    if match:
        return match.group(1)

    return None