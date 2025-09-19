import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import base64

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.gmail_fetcher import (
    search_message_by_message_id_header,
    fetch_message_by_id,
    extract_email_content,
    extract_message_body,
    strip_html_tags,
    fetch_email_by_message_id_header,
    fetch_email_by_gmail_id
)
from modules.google_auth import authenticate_google_services
from googleapiclient.errors import HttpError


class TestGmailFetcherUnit(unittest.TestCase):
    """Unit tests for gmail_fetcher module functions."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_message_id_header = "684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail"
        self.sample_gmail_message_id = "1995b3c89509dde1"
        self.sample_gmail_message = {
            'id': '1995b3c89509dde1',
            'threadId': 'FMfcgzQcpKXrSxfnbLfGFDksqcvNBgKj',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Meeting Invite'},
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'Date', 'value': 'Mon, 15 Jan 2024 10:00:00 +0000'},
                    {'name': 'Message-ID', 'value': self.sample_message_id_header}
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

    @patch('modules.gmail_fetcher.authenticate_google_services')
    @patch('modules.gmail_fetcher.build')
    def test_search_message_by_message_id_header_success(self, mock_build, mock_auth):
        """Test successful message search using Message-ID header."""
        # Setup
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock search results
        mock_list = MagicMock()
        mock_list.execute.return_value = {'messages': [{'id': self.sample_gmail_message_id}]}
        mock_service.users().messages().list.return_value = mock_list

        # Mock message get
        mock_get = MagicMock()
        mock_get.execute.return_value = self.sample_gmail_message
        mock_service.users().messages().get.return_value = mock_get

        # Execute
        result = search_message_by_message_id_header(self.sample_message_id_header)

        # Assert
        self.assertEqual(result, self.sample_gmail_message)
        mock_service.users().messages().list.assert_called_once_with(
            userId='me',
            q=f'rfc822msgid:{self.sample_message_id_header}',
            maxResults=1
        )
        mock_service.users().messages().get.assert_called_once_with(
            userId='me',
            id=self.sample_gmail_message_id,
            format='full'
        )

    @patch('modules.gmail_fetcher.authenticate_google_services')
    @patch('modules.gmail_fetcher.build')
    def test_search_message_by_message_id_header_not_found(self, mock_build, mock_auth):
        """Test message search when Message-ID header is not found."""
        # Setup
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock empty search results
        mock_list = MagicMock()
        mock_list.execute.return_value = {'messages': []}
        mock_service.users().messages().list.return_value = mock_list

        # Execute
        result = search_message_by_message_id_header(self.sample_message_id_header)

        # Assert
        self.assertIsNone(result)

    @patch('modules.gmail_fetcher.authenticate_google_services')
    @patch('modules.gmail_fetcher.build')
    def test_fetch_message_by_id_success(self, mock_build, mock_auth):
        """Test successful message fetching by Gmail API message ID."""
        # Setup
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_get = MagicMock()
        mock_get.execute.return_value = self.sample_gmail_message
        mock_service.users().messages().get.return_value = mock_get

        # Execute
        result = fetch_message_by_id(self.sample_gmail_message_id)

        # Assert
        self.assertEqual(result, self.sample_gmail_message)
        mock_service.users().messages().get.assert_called_once_with(
            userId='me',
            id=self.sample_gmail_message_id,
            format='full'
        )

    @patch('modules.gmail_fetcher.authenticate_google_services')
    @patch('modules.gmail_fetcher.build')
    def test_fetch_message_by_id_not_found(self, mock_build, mock_auth):
        """Test message fetching when message ID doesn't exist."""
        # Setup
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create mock HttpError for 404
        mock_error = HttpError(MagicMock(status=404), b'Not Found')
        mock_service.users().messages().get().execute.side_effect = mock_error

        # Execute & Assert
        with self.assertRaises(Exception) as context:
            fetch_message_by_id(self.sample_gmail_message_id)

        self.assertIn("not found", str(context.exception))

    def test_extract_email_content(self):
        """Test extraction of email content from Gmail message object."""
        # Execute
        result = extract_email_content(self.sample_gmail_message)

        # Assert
        self.assertIn("Subject: Test Meeting Invite", result)
        self.assertIn("From: sender@example.com", result)
        self.assertIn("Date: Mon, 15 Jan 2024 10:00:00 +0000", result)
        self.assertIn(f"Message-ID: {self.sample_message_id_header}", result)
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

    @patch('modules.gmail_fetcher.search_message_by_message_id_header')
    @patch('modules.gmail_fetcher.extract_email_content')
    def test_fetch_email_by_message_id_header_success(self, mock_extract, mock_search):
        """Test complete workflow for fetching email by Message-ID header."""
        # Setup
        expected_content = "Subject: Test Email\n\nEmail content here"
        mock_search.return_value = self.sample_gmail_message
        mock_extract.return_value = expected_content

        # Execute
        result = fetch_email_by_message_id_header(self.sample_message_id_header)

        # Assert
        self.assertEqual(result, expected_content)
        mock_search.assert_called_once_with(self.sample_message_id_header)
        mock_extract.assert_called_once_with(self.sample_gmail_message)

    @patch('modules.gmail_fetcher.search_message_by_message_id_header')
    def test_fetch_email_by_message_id_header_not_found(self, mock_search):
        """Test workflow when Message-ID header is not found."""
        # Setup
        mock_search.return_value = None

        # Execute & Assert
        with self.assertRaises(Exception) as context:
            fetch_email_by_message_id_header(self.sample_message_id_header)

        self.assertIn("No message found with Message-ID header", str(context.exception))

    @patch('modules.gmail_fetcher.fetch_message_by_id')
    @patch('modules.gmail_fetcher.extract_email_content')
    def test_fetch_email_by_gmail_id_success(self, mock_extract, mock_fetch):
        """Test complete workflow for fetching email by Gmail API message ID."""
        # Setup
        expected_content = "Subject: Test Email\n\nEmail content here"
        mock_fetch.return_value = self.sample_gmail_message
        mock_extract.return_value = expected_content

        # Execute
        result = fetch_email_by_gmail_id(self.sample_gmail_message_id)

        # Assert
        self.assertEqual(result, expected_content)
        mock_fetch.assert_called_once_with(self.sample_gmail_message_id)
        mock_extract.assert_called_once_with(self.sample_gmail_message)


if __name__ == '__main__':
    unittest.main()