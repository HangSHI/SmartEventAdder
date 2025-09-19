"""
Test Gmail messages.get() API method and Message-ID header handling.

IMPORTANT DISCOVERIES:
Gmail uses THREE different ID formats that are NOT interchangeable:

1. Gmail URL IDs (32 chars): FMfcgzQcpnPVtskckfTVKvTdmrrjVXGf
   - Found in Gmail web interface URLs
   - CANNOT be used directly with Gmail API
   - Will return "Invalid id value" error

2. Gmail API Message IDs (16 chars): 1995785e0194fbb3
   - Used by Gmail API for messages.get() calls
   - These are the ONLY IDs that work with direct API calls
   - Different from URL IDs completely

3. Email Message-ID Headers (email format): 2b630e07-5cd7-4791-9ff1-a4d0a58a56e3@seg.co.jp
   - Standard email Message-ID header from SMTP
   - CANNOT be used directly with messages.get()
   - Must be searched using: rfc822msgid:message-id-here

KEY FINDINGS:
- Gemini's recommendation to use URL IDs directly is INCORRECT
- The proper approach for Message-ID headers is to search first, then get
- Only Gmail API message IDs work with direct messages.get() calls
- Gmail web interface uses different internal IDs than the API
"""

import json
import base64
from modules.gmail_fetcher import authenticate_gmail
from googleapiclient.discovery import build


def test_gmail_message_get():
    """
    Test Gmail messages.get() API with Message-ID header (WILL FAIL).

    This test demonstrates why Message-ID headers cannot be used directly
    with Gmail API's messages.get() method. This is a common misconception.

    Expected Result: HttpError 400 "Invalid id value"
    """

    # Message-ID header from actual email (this WILL FAIL when used directly)
    message_id = '2b630e07-5cd7-4791-9ff1-a4d0a58a56e3@seg.co.jp'

    try:
        print(f"Testing Gmail messages.get() API")
        print(f"Message ID: {message_id}")
        print("=" * 80)

        # Authenticate with Gmail API
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

        # Call messages.get() API as recommended by Gemini
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'  # Get full message content
        ).execute()

        print("✅ SUCCESS: Gmail messages.get() API call successful!")
        print("=" * 80)

        # Display message structure
        print(f"Message ID: {message.get('id')}")
        print(f"Thread ID: {message.get('threadId')}")
        print(f"Labels: {message.get('labelIds', [])}")
        print(f"Snippet: {message.get('snippet', 'N/A')[:100]}...")
        print(f"Size Estimate: {message.get('sizeEstimate')} bytes")

        # Show payload structure
        payload = message.get('payload', {})
        print(f"MIME Type: {payload.get('mimeType')}")
        print(f"Headers count: {len(payload.get('headers', []))}")

        # Try to decode body content if available
        body = payload.get('body', {})
        if body.get('data'):
            try:
                decoded_content = base64.urlsafe_b64decode(body['data']).decode('utf-8')
                print(f"Decoded content preview: {decoded_content[:200]}...")
            except Exception as decode_error:
                print(f"Could not decode body content: {decode_error}")

        print("=" * 80)
        print("📋 FULL JSON RESPONSE:")
        print(json.dumps(message, indent=2, ensure_ascii=False))

        return message

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"This confirms the Message-ID header '{message_id}' cannot be used directly")
        print("with Gmail API. Gmail API uses its own internal message IDs.")
        return None


def search_message_by_message_id_header():
    """
    Search for message using Message-ID header (CORRECT APPROACH).

    This demonstrates the proper way to find Gmail messages when you have
    the Message-ID header from an email. Uses Gmail's search functionality
    with the 'rfc822msgid:' operator.

    Steps:
    1. Use messages.list() with 'rfc822msgid:message-id-here' search query
    2. Get Gmail API message ID from search results
    3. Use messages.get() with the Gmail API message ID

    Expected Result: SUCCESS - finds and retrieves the message
    """

    message_id_header = '2b630e07-5cd7-4791-9ff1-a4d0a58a56e3@seg.co.jp'

    try:
        print("\n" + "=" * 80)
        print("Searching for message using Message-ID header")
        print("=" * 80)

        # Authenticate
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

        # Search for message by Message-ID header
        # Use Gmail search query to find message with specific Message-ID
        search_query = f'rfc822msgid:{message_id_header}'
        print(f"Search query: {search_query}")

        result = service.users().messages().list(
            userId='me',
            q=search_query,
            maxResults=1
        ).execute()

        messages = result.get('messages', [])

        if messages:
            gmail_message_id = messages[0]['id']
            print(f"✅ FOUND! Gmail API message ID: {gmail_message_id}")

            # Get the full message content
            message = service.users().messages().get(
                userId='me',
                id=gmail_message_id,
                format='full'
            ).execute()

            print(f"Message snippet: {message.get('snippet', 'N/A')[:100]}...")

            # Look for the Message-ID header in the email headers
            payload = message.get('payload', {})
            headers = payload.get('headers', [])

            for header in headers:
                if header.get('name', '').lower() == 'message-id':
                    print(f"Found Message-ID header: {header.get('value')}")
                    break

            print("=" * 80)
            print("📋 FULL MESSAGE JSON:")
            print(json.dumps(message, indent=2, ensure_ascii=False))

            return message

        else:
            print(f"❌ No message found with Message-ID: {message_id_header}")
            print("This message may not exist in your Gmail account or may be in a different folder.")
            return None

    except Exception as e:
        print(f"❌ ERROR searching for message: {e}")
        return None


def test_with_real_message_id():
    """
    Test with a real Gmail API message ID (DEMONSTRATES WORKING APPROACH).

    This shows how messages.get() works when you have the correct Gmail API
    message ID format. These IDs are obtained from:
    - messages.list() API calls
    - threads.get() API calls
    - Gmail API search results

    Expected Result: SUCCESS - retrieves message directly
    """

    try:
        print("\n" + "=" * 80)
        print("Testing with REAL message ID from Gmail account")
        print("=" * 80)

        # Authenticate and get a real message ID
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

        # Get recent messages
        result = service.users().messages().list(userId='me', maxResults=1).execute()
        messages = result.get('messages', [])

        if messages:
            real_message_id = messages[0]['id']
            print(f"Using real message ID: {real_message_id}")

            # Test messages.get() with real ID
            message = service.users().messages().get(
                userId='me',
                id=real_message_id,
                format='full'
            ).execute()

            print("✅ SUCCESS: Real message ID works!")
            print(f"Message snippet: {message.get('snippet', 'N/A')[:100]}...")

            # Compare ID formats
            print(f"\nID Format Comparison:")
            print(f"Email Message-ID: 2b630e07-5cd7-4791-9ff1-a4d0a58a56e3@seg.co.jp (length: {len('2b630e07-5cd7-4791-9ff1-a4d0a58a56e3@seg.co.jp')})")
            print(f"Real message ID:  {real_message_id} (length: {len(real_message_id)})")

        else:
            print("No messages found in Gmail account")

    except Exception as e:
        print(f"❌ ERROR with real message ID: {e}")


if __name__ == "__main__":
    print("Gmail Messages API Test - ID Format Analysis")
    print("=" * 80)
    print("TESTING DIFFERENT GMAIL ID FORMATS:")
    print("1. Message-ID Header → Search Required")
    print("2. Gmail URL ID → Does Not Work")
    print("3. Gmail API ID → Direct Access Works")
    print("=" * 80)

    # Test 1: Demonstrate Message-ID header failure with direct approach
    print("\n🔴 EXPECTED FAILURE: Message-ID header with messages.get()")
    test_gmail_message_get()

    # Test 2: Demonstrate correct approach for Message-ID headers
    print("\n🟢 CORRECT APPROACH: Message-ID header with search")
    search_message_by_message_id_header()

    # Test 3: Show working approach with real Gmail API message ID
    print("\n🟢 WORKING APPROACH: Real Gmail API message ID")
    test_with_real_message_id()

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("✅ Only Gmail API message IDs work with direct messages.get()")
    print("✅ Message-ID headers require search-first approach")
    print("❌ Gmail URL IDs cannot be used with Gmail API")
    print("=" * 80)