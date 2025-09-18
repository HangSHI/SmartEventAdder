import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import base64

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.gmail_fetcher import (
    authenticate_gmail,
    fetch_email_by_id,
    fetch_email_by_url,
    resolve_gmail_url_to_message_id,
    extract_email_content,
    extract_message_body,
    strip_html_tags,
    validate_message_id,
    extract_message_id_from_url
)
from googleapiclient.errors import HttpError


class TestGmailFetcherUnit(unittest.TestCase):
    """Unit tests for gmail_fetcher module functions."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_message_id = "18c8f4a2b5d6789a"
        self.sample_gmail_message = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Meeting Invite'},
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'Date', 'value': 'Mon, 15 Jan 2024 10:00:00 +0000'}
                ],
                'mimeType': 'text/plain',
                'body': {
                    'data': base64.urlsafe_b64encode(b'Meeting tomorrow at 2pm in room A').decode()
                }
            }
        }

    @patch('modules.gmail_fetcher.os.path.exists')
    @patch('modules.gmail_fetcher.Credentials.from_authorized_user_file')
    def test_authenticate_gmail_with_existing_valid_token(self, mock_from_file, mock_exists):
        """Test authenticate_gmail function when valid token.json exists."""
        # Setup
        mock_exists.return_value = True
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_from_file.return_value = mock_creds

        # Execute
        result = authenticate_gmail()

        # Assert
        self.assertEqual(result, mock_creds)
        mock_exists.assert_called_once_with('token.json')
        mock_from_file.assert_called_once()

    @patch('modules.gmail_fetcher.os.path.exists')
    @patch('modules.gmail_fetcher.InstalledAppFlow.from_client_secrets_file')
    @patch('builtins.open', new_callable=mock_open)
    def test_authenticate_gmail_new_credentials(self, mock_file, mock_flow, mock_exists):
        """Test authenticate_gmail function when no valid credentials exist."""
        # Setup
        mock_exists.return_value = False
        mock_flow_instance = MagicMock()
        mock_creds = MagicMock()
        mock_creds.to_json.return_value = '{"token": "test"}'
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.return_value = mock_flow_instance

        # Execute
        result = authenticate_gmail()

        # Assert
        self.assertEqual(result, mock_creds)
        mock_flow.assert_called_once()
        mock_file.assert_called_once_with('token.json', 'w')

    @patch('modules.gmail_fetcher.authenticate_gmail')
    @patch('modules.gmail_fetcher.build')
    def test_fetch_email_by_id_success(self, mock_build, mock_auth):
        """Test successful email fetching by message ID."""
        # Setup
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create a proper mock chain for the API call
        mock_get = MagicMock()
        mock_get.execute.return_value = self.sample_gmail_message
        mock_service.users().messages().get.return_value = mock_get

        # Execute
        result = fetch_email_by_id(self.sample_message_id)

        # Assert
        self.assertIn("Subject: Test Meeting Invite", result)
        self.assertIn("From: sender@example.com", result)
        self.assertIn("Meeting tomorrow at 2pm in room A", result)
        mock_service.users().messages().get.assert_called_once_with(
            userId='me',
            id=self.sample_message_id,
            format='full'
        )

    @patch('modules.gmail_fetcher.authenticate_gmail')
    @patch('modules.gmail_fetcher.build')
    def test_fetch_email_by_id_not_found(self, mock_build, mock_auth):
        """Test email fetching when message ID doesn't exist."""
        # Setup
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create mock HttpError for 404
        mock_error = HttpError(MagicMock(status=404), b'Not Found')
        mock_service.users().messages().get().execute.side_effect = mock_error

        # Execute & Assert
        with self.assertRaises(Exception) as context:
            fetch_email_by_id(self.sample_message_id)

        self.assertIn("not found", str(context.exception))

    @patch('modules.gmail_fetcher.authenticate_gmail')
    @patch('modules.gmail_fetcher.build')
    def test_fetch_email_by_id_access_denied(self, mock_build, mock_auth):
        """Test email fetching when access is denied."""
        # Setup
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create mock HttpError for 403
        mock_error = HttpError(MagicMock(status=403), b'Access Denied')
        mock_service.users().messages().get().execute.side_effect = mock_error

        # Execute & Assert
        with self.assertRaises(Exception) as context:
            fetch_email_by_id(self.sample_message_id)

        self.assertIn("Access denied", str(context.exception))

    def test_extract_email_content(self):
        """Test extraction of email content from Gmail message object."""
        # Execute
        result = extract_email_content(self.sample_gmail_message)

        # Assert
        self.assertIn("Subject: Test Meeting Invite", result)
        self.assertIn("From: sender@example.com", result)
        self.assertIn("Date: Mon, 15 Jan 2024 10:00:00 +0000", result)
        self.assertIn("Meeting tomorrow at 2pm in room A", result)

    def test_extract_message_body_plain_text(self):
        """Test extraction of plain text message body."""
        # Setup
        payload = {
            'mimeType': 'text/plain',
            'body': {
                'data': base64.urlsafe_b64encode(b'This is a test message').decode()
            }
        }

        # Execute
        result = extract_message_body(payload)

        # Assert
        self.assertEqual(result, 'This is a test message')

    def test_extract_message_body_multipart(self):
        """Test extraction from multipart message."""
        # Setup
        payload = {
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {
                        'data': base64.urlsafe_b64encode(b'Part 1 ').decode()
                    }
                },
                {
                    'mimeType': 'text/plain',
                    'body': {
                        'data': base64.urlsafe_b64encode(b'Part 2').decode()
                    }
                }
            ]
        }

        # Execute
        result = extract_message_body(payload)

        # Assert
        self.assertEqual(result, 'Part 1 Part 2')

    def test_strip_html_tags(self):
        """Test HTML tag removal from email content."""
        # Setup
        html_content = '<p>Hello <b>world</b>!</p><br>&nbsp;&amp;'

        # Execute
        result = strip_html_tags(html_content)

        # Assert
        self.assertEqual(result, 'Hello world! &')

    def test_validate_message_id_valid(self):
        """Test validation of valid Gmail message IDs."""
        # Test cases
        valid_ids = [
            "18c8f4a2b5d6789a",
            "1234567890abcdef",
            "ABCDEF1234567890abcdef"
        ]

        for message_id in valid_ids:
            with self.subTest(message_id=message_id):
                self.assertTrue(validate_message_id(message_id))

    def test_validate_message_id_invalid(self):
        """Test validation of invalid Gmail message IDs."""
        # Test cases
        invalid_ids = [
            "123",  # Too short
            "invalid-id-with-dashes",  # Contains dashes
            "notahexstring",  # Not hex
            "",  # Empty
            "123@456"  # Contains special characters
        ]

        for message_id in invalid_ids:
            with self.subTest(message_id=message_id):
                self.assertFalse(validate_message_id(message_id))

    def test_extract_message_id_from_url_success(self):
        """Test extracting message ID from Gmail URLs."""
        # Test cases
        test_cases = [
            ("https://mail.google.com/mail/u/0/#inbox/18c8f4a2b5d6789a", "18c8f4a2b5d6789a"),
            ("https://mail.google.com/mail/u/0/#sent/1234567890abcdef", "1234567890abcdef"),
            ("https://mail.google.com/mail/u/0/#drafts/abcdef1234567890", "abcdef1234567890"),
        ]

        for url, expected_id in test_cases:
            with self.subTest(url=url):
                result = extract_message_id_from_url(url)
                self.assertEqual(result, expected_id)

    def test_extract_message_id_from_url_invalid(self):
        """Test extracting message ID from invalid URLs."""
        # Test cases
        invalid_urls = [
            "https://mail.google.com/mail/u/0/#inbox/",  # No ID
            "https://example.com/not-gmail",  # Not Gmail
            "invalid-url",  # Not a URL
            "",  # Empty
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                result = extract_message_id_from_url(url)
                self.assertIsNone(result)

    @patch('modules.gmail_fetcher.resolve_gmail_url_to_message_id')
    @patch('modules.gmail_fetcher.fetch_email_by_id')
    def test_fetch_email_by_url_success(self, mock_fetch_by_id, mock_resolve):
        """Test successful email fetching by Gmail URL."""
        # Setup
        gmail_url = "https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr"
        resolved_id = "1995b3c89509dde1"
        expected_content = "Subject: Test Email\n\nEmail content here"

        mock_resolve.return_value = resolved_id
        mock_fetch_by_id.return_value = expected_content

        # Execute
        result = fetch_email_by_url(gmail_url)

        # Assert
        self.assertEqual(result, expected_content)
        mock_resolve.assert_called_once_with(gmail_url)
        mock_fetch_by_id.assert_called_once_with(resolved_id)

    @patch('modules.gmail_fetcher.resolve_gmail_url_to_message_id')
    def test_fetch_email_by_url_resolve_failure(self, mock_resolve):
        """Test email fetching when URL cannot be resolved."""
        # Setup
        gmail_url = "https://mail.google.com/mail/u/0/#inbox/invalid"
        mock_resolve.return_value = None

        # Execute & Assert
        with self.assertRaises(Exception) as context:
            fetch_email_by_url(gmail_url)

        self.assertIn("Could not resolve Gmail URL to message ID", str(context.exception))
        mock_resolve.assert_called_once_with(gmail_url)

    @patch('modules.gmail_fetcher.authenticate_gmail')
    @patch('modules.gmail_fetcher.build')
    @patch('modules.gmail_fetcher.extract_message_id_from_url')
    def test_resolve_gmail_url_to_message_id_success(self, mock_extract, mock_build, mock_auth):
        """Test successful Gmail URL to message ID resolution."""
        # Setup
        gmail_url = "https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr"
        url_id = "FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr"
        api_message_id = "1995b3c89509dde1"

        mock_extract.return_value = url_id
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create proper mock chain for the API call
        mock_list = MagicMock()
        mock_list.execute.return_value = {'messages': [{'id': api_message_id}]}
        mock_service.users().messages().list.return_value = mock_list

        # Execute
        result = resolve_gmail_url_to_message_id(gmail_url)

        # Assert
        self.assertEqual(result, api_message_id)
        mock_extract.assert_called_once_with(gmail_url)
        mock_service.users().messages().list.assert_called_once_with(
            userId='me',
            maxResults=100
        )

    @patch('modules.gmail_fetcher.extract_message_id_from_url')
    def test_resolve_gmail_url_to_message_id_invalid_url(self, mock_extract):
        """Test Gmail URL resolution with invalid URL."""
        # Setup
        gmail_url = "https://invalid-url.com"
        mock_extract.return_value = None

        # Execute
        result = resolve_gmail_url_to_message_id(gmail_url)

        # Assert
        self.assertIsNone(result)
        mock_extract.assert_called_once_with(gmail_url)

    @patch('modules.gmail_fetcher.authenticate_gmail')
    @patch('modules.gmail_fetcher.build')
    @patch('modules.gmail_fetcher.extract_message_id_from_url')
    def test_resolve_gmail_url_to_message_id_no_messages(self, mock_extract, mock_build, mock_auth):
        """Test Gmail URL resolution when no messages found."""
        # Setup
        gmail_url = "https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr"
        url_id = "FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr"

        mock_extract.return_value = url_id
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create proper mock chain for the API call
        mock_list = MagicMock()
        mock_list.execute.return_value = {'messages': []}
        mock_service.users().messages().list.return_value = mock_list

        # Execute
        result = resolve_gmail_url_to_message_id(gmail_url)

        # Assert
        self.assertIsNone(result)


class TestGmailFetcherIntegration(unittest.TestCase):
    """Integration tests for gmail_fetcher module with mocked Gmail API."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_html_message = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'HTML Email Test'},
                    {'name': 'From', 'value': 'test@example.com'},
                ],
                'mimeType': 'text/html',
                'body': {
                    'data': base64.urlsafe_b64encode(
                        b'<html><body><p>Meeting <b>tomorrow</b> at 2pm</p></body></html>'
                    ).decode()
                }
            }
        }

    def test_extract_html_email_content(self):
        """Test extraction of HTML email content with tag stripping."""
        # Execute
        result = extract_email_content(self.sample_html_message)

        # Assert
        self.assertIn("Subject: HTML Email Test", result)
        self.assertIn("Meeting tomorrow at 2pm", result)
        # Ensure HTML tags are stripped
        self.assertNotIn("<html>", result)
        self.assertNotIn("<body>", result)
        self.assertNotIn("<p>", result)
        self.assertNotIn("<b>", result)


if __name__ == '__main__':
    unittest.main()