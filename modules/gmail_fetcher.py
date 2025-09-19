from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .google_auth import authenticate_google_services


def search_message_by_message_id_header(message_id_header):
    """
    Search for Gmail message using Message-ID header.

    This is the correct approach when you have an email's Message-ID header.
    Gmail API requires searching first, then fetching the message.

    Args:
        message_id_header (str): Email Message-ID header (e.g., "abc@example.com")

    Returns:
        dict: Gmail API message object or None if not found

    Raises:
        Exception: If search fails
    """
    try:
        # Authenticate and build the service
        creds = authenticate_google_services()
        service = build('gmail', 'v1', credentials=creds)

        # Search for message using rfc822msgid: operator
        search_query = f'rfc822msgid:{message_id_header}'
        print(f"🔍 Searching with query: {search_query}")

        result = service.users().messages().list(
            userId='me',
            q=search_query,
            maxResults=1
        ).execute()

        messages = result.get('messages', [])

        if messages:
            gmail_message_id = messages[0]['id']
            print(f"✅ Found Gmail API message ID: {gmail_message_id}")

            # Get the full message content
            message = service.users().messages().get(
                userId='me',
                id=gmail_message_id,
                format='full'
            ).execute()

            return message
        else:
            print(f"❌ No message found with Message-ID header: {message_id_header}")
            return None

    except HttpError as error:
        if error.resp.status == 403:
            raise Exception("Access denied. Please ensure Gmail API is enabled and you have proper permissions.")
        else:
            raise Exception(f"Gmail API error: {error}")
    except Exception as e:
        raise Exception(f"Failed to search for message with header {message_id_header}: {str(e)}")


def fetch_message_by_id(gmail_message_id):
    """
    Fetch Gmail message content using Gmail API message ID.

    Use this when you have a real Gmail API message ID (16 chars, alphanumeric).

    Args:
        gmail_message_id (str): Gmail API message ID (e.g., "1995b3c89509dde1")

    Returns:
        dict: Gmail API message object

    Raises:
        Exception: If message cannot be fetched
    """
    try:
        # Authenticate and build the service
        creds = authenticate_google_services()
        service = build('gmail', 'v1', credentials=creds)

        print(f"🔗 Fetching message with ID: {gmail_message_id}")

        # Get the message
        message = service.users().messages().get(
            userId='me',
            id=gmail_message_id,
            format='full'
        ).execute()

        print(f"✅ Message fetched successfully!")
        return message

    except HttpError as error:
        if error.resp.status == 404:
            raise Exception(f"Message with ID '{gmail_message_id}' not found. Please check the message ID.")
        elif error.resp.status == 403:
            raise Exception("Access denied. Please ensure Gmail API is enabled and you have proper permissions.")
        else:
            raise Exception(f"Gmail API error: {error}")
    except Exception as e:
        raise Exception(f"Failed to fetch message {gmail_message_id}: {str(e)}")


def extract_email_content(message):
    """
    Extract readable content from Gmail message object.

    Args:
        message (dict): Gmail API message object

    Returns:
        str: Formatted email content with subject, from, date, and body
    """
    # Get headers
    headers = message.get('payload', {}).get('headers', [])
    subject = ""
    sender = ""
    date = ""
    message_id_header = ""

    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')

        if name == 'subject':
            subject = value
        elif name == 'from':
            sender = value
        elif name == 'date':
            date = value
        elif name == 'message-id':
            message_id_header = value

    # Get email body
    body = extract_message_body(message.get('payload', {}))

    # Format the email content
    email_content = f"Subject: {subject}\n"
    if sender:
        email_content += f"From: {sender}\n"
    if date:
        email_content += f"Date: {date}\n"
    if message_id_header:
        email_content += f"Message-ID: {message_id_header}\n"
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
    import base64

    body = ""

    # Check if payload has parts (multipart message)
    if 'parts' in payload:
        for part in payload['parts']:
            # Recursively extract from parts
            body += extract_message_body(part)
    else:
        # Single part message
        mime_type = payload.get('mimeType', '')

        if mime_type in ['text/plain', 'text/html']:
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


def fetch_email_by_message_id_header(message_id_header):
    """
    Complete workflow to fetch email content using Message-ID header.

    This is the main function for the Message-ID header workflow:
    1. Search for message using Message-ID header
    2. Extract readable email content

    Args:
        message_id_header (str): Email Message-ID header

    Returns:
        str: Formatted email content

    Raises:
        Exception: If email cannot be found or fetched
    """
    try:
        # Step 1: Search for message by Message-ID header
        message = search_message_by_message_id_header(message_id_header)
        if not message:
            raise Exception(f"No message found with Message-ID header: {message_id_header}")

        # Step 2: Extract readable content
        email_content = extract_email_content(message)

        return email_content

    except Exception as e:
        raise Exception(f"Failed to fetch email by Message-ID header {message_id_header}: {str(e)}")


def fetch_email_by_gmail_id(gmail_message_id):
    """
    Complete workflow to fetch email content using Gmail API message ID.

    This is the main function for the Gmail API message ID workflow:
    1. Fetch message using Gmail API message ID
    2. Extract readable email content

    Args:
        gmail_message_id (str): Gmail API message ID

    Returns:
        str: Formatted email content

    Raises:
        Exception: If email cannot be fetched
    """
    try:
        # Step 1: Fetch message by Gmail API message ID
        message = fetch_message_by_id(gmail_message_id)

        # Step 2: Extract readable content
        email_content = extract_email_content(message)

        return email_content

    except Exception as e:
        raise Exception(f"Failed to fetch email by Gmail message ID {gmail_message_id}: {str(e)}")