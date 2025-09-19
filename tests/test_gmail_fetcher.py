import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.gmail_fetcher import (
    authenticate_gmail,
    extract_thread_id_from_url,
    fetch_gmail_thread_json
)
from googleapiclient.errors import HttpError


class TestGmailFetcherUnit(unittest.TestCase):
    """Unit tests for gmail_fetcher module functions."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_gmail_url = "https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpKXrSxfnbLfGFDksqcvNBgKj"
        self.sample_thread_id = "FMfcgzQcpKXrSxfnbLfGFDksqcvNBgKj"

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

    def test_extract_thread_id_from_url_success(self):
        """Test extracting thread ID from Gmail URLs."""
        # Test cases
        test_cases = [
            ("https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpKXrSxfnbLfGFDksqcvNBgKj", "FMfcgzQcpKXrSxfnbLfGFDksqcvNBgKj"),
            ("https://mail.google.com/mail/u/0/#sent/FMfcgzQbgcQTZvmQLHXPxgKmCvJZFGKp", "FMfcgzQbgcQTZvmQLHXPxgKmCvJZFGKp"),
            ("https://mail.google.com/mail/u/0/#search/予約/FMfcgzQbfnxmdnbjNwSnLThtCtPmmfDz", "FMfcgzQbfnxmdnbjNwSnLThtCtPmmfDz"),
        ]

        for url, expected_id in test_cases:
            with self.subTest(url=url):
                result = extract_thread_id_from_url(url)
                self.assertEqual(result, expected_id)

    def test_extract_thread_id_from_url_invalid(self):
        """Test extracting thread ID from invalid URLs."""
        # Test cases
        invalid_urls = [
            "https://mail.google.com/mail/u/0/#inbox/",  # No ID
            "https://example.com/not-gmail",  # Not Gmail
            "invalid-url",  # Not a URL
            "",  # Empty
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                result = extract_thread_id_from_url(url)
                self.assertIsNone(result)

    @patch('modules.gmail_fetcher.authenticate_gmail')
    @patch('modules.gmail_fetcher.build')
    @patch('modules.gmail_fetcher.extract_thread_id_from_url')
    def test_fetch_gmail_thread_json_success(self, mock_extract, mock_build, mock_auth):
        """Test successful Gmail thread JSON fetching."""
        # Setup
        gmail_url = "https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpKXrSxfnbLfGFDksqcvNBgKj"
        thread_id = "FMfcgzQcpKXrSxfnbLfGFDksqcvNBgKj"

        mock_extract.return_value = thread_id
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock thread JSON response
        expected_thread_json = {
            'id': thread_id,
            'historyId': '12345',
            'messages': [
                {
                    'id': '1995b3c89509dde1',
                    'threadId': thread_id,
                    'payload': {
                        'headers': [
                            {'name': 'Subject', 'value': 'Test Thread'},
                        ]
                    }
                }
            ]
        }

        mock_thread_get = MagicMock()
        mock_thread_get.execute.return_value = expected_thread_json
        mock_service.users().threads().get.return_value = mock_thread_get

        # Execute
        result = fetch_gmail_thread_json(gmail_url)

        # Assert
        self.assertEqual(result, expected_thread_json)
        mock_extract.assert_called_once_with(gmail_url)
        mock_service.users().threads().get.assert_called_once_with(
            userId='me',
            id=thread_id,
            format='full'
        )

    @patch('modules.gmail_fetcher.extract_thread_id_from_url')
    def test_fetch_gmail_thread_json_invalid_url(self, mock_extract):
        """Test Gmail thread JSON fetching with invalid URL."""
        # Setup
        gmail_url = "https://invalid-url.com"
        mock_extract.return_value = None

        # Execute & Assert
        with self.assertRaises(Exception) as context:
            fetch_gmail_thread_json(gmail_url)

        self.assertIn("Could not extract thread ID from Gmail URL", str(context.exception))
        mock_extract.assert_called_once_with(gmail_url)

    @patch('modules.gmail_fetcher.authenticate_gmail')
    @patch('modules.gmail_fetcher.build')
    @patch('modules.gmail_fetcher.extract_thread_id_from_url')
    def test_fetch_gmail_thread_json_thread_not_found(self, mock_extract, mock_build, mock_auth):
        """Test Gmail thread JSON fetching when thread is not found."""
        # Setup
        gmail_url = "https://mail.google.com/mail/u/0/#inbox/nonexistent"
        thread_id = "nonexistent"

        mock_extract.return_value = thread_id
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock 404 HttpError
        mock_error = HttpError(MagicMock(status=404), b'Not Found')
        mock_thread_get = MagicMock()
        mock_thread_get.execute.side_effect = mock_error
        mock_service.users().threads().get.return_value = mock_thread_get

        # Execute & Assert
        with self.assertRaises(Exception) as context:
            fetch_gmail_thread_json(gmail_url)

        self.assertIn("not found", str(context.exception))

    @patch('modules.gmail_fetcher.authenticate_gmail')
    @patch('modules.gmail_fetcher.build')
    @patch('modules.gmail_fetcher.extract_thread_id_from_url')
    def test_fetch_gmail_thread_json_access_denied(self, mock_extract, mock_build, mock_auth):
        """Test Gmail thread JSON fetching when access is denied."""
        # Setup
        gmail_url = "https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpKXrSxfnbLfGFDksqcvNBgKj"
        thread_id = "FMfcgzQcpKXrSxfnbLfGFDksqcvNBgKj"

        mock_extract.return_value = thread_id
        mock_auth.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock 403 HttpError
        mock_error = HttpError(MagicMock(status=403), b'Access Denied')
        mock_thread_get = MagicMock()
        mock_thread_get.execute.side_effect = mock_error
        mock_service.users().threads().get.return_value = mock_thread_get

        # Execute & Assert
        with self.assertRaises(Exception) as context:
            fetch_gmail_thread_json(gmail_url)

        self.assertIn("Access denied", str(context.exception))


if __name__ == '__main__':
    unittest.main()