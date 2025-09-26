import unittest
import os
import sys
import logging
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

# Add the parent directory to the path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    setup_logging,
    load_environment,
    get_email_input,
    validate_email_input,
    validate_extracted_data,
    display_event_details,
    get_user_confirmation,
    create_calendar_event,
    is_message_id_header
)


class TestMainFunctions(unittest.TestCase):
    """Unit tests for main.py functions with comprehensive mocking."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_event_data = {
            'summary': 'Test Meeting',
            'date': '2024-01-15',
            'start_time': '14:30',
            'location': 'Conference Room A'
        }

        self.incomplete_event_data = {
            'summary': 'Test Meeting',
            'date': None,
            'start_time': '14:30',
            'location': 'Conference Room A'
        }

        self.sample_email = """
        Hi team,

        Please join our weekly meeting on January 15, 2024 at 2:30 PM.
        We'll meet in Conference Room A.

        Best regards,
        Manager
        """

    def test_setup_logging(self):
        """Test logging configuration setup."""
        logger = setup_logging()

        # Verify logger is created and properly named
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, 'main')

        # Verify the function returns a logger (basic functionality test)
        self.assertIsNotNone(logger)

    @patch.dict(os.environ, {
        'GOOGLE_CLOUD_PROJECT_ID': 'test-project-123',
        'GOOGLE_CLOUD_LOCATION': 'us-central1'
    })
    @patch('main.load_dotenv')
    def test_load_environment_success(self, mock_load_dotenv):
        """Test successful environment loading."""
        config = load_environment()

        self.assertEqual(config['project_id'], 'test-project-123')
        self.assertEqual(config['location'], 'us-central1')
        mock_load_dotenv.assert_called_once()

    @patch.dict(os.environ, {'GOOGLE_CLOUD_LOCATION': 'us-central1'}, clear=True)
    @patch('main.load_dotenv')
    def test_load_environment_missing_project_id(self, mock_load_dotenv):
        """Test environment loading with missing project ID."""
        with self.assertRaises(ValueError) as context:
            load_environment()

        self.assertIn("GOOGLE_CLOUD_PROJECT_ID not found", str(context.exception))
        self.assertIn("setup_gcloud.sh", str(context.exception))

    @patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT_ID': 'test-project'}, clear=True)
    @patch('main.load_dotenv')
    def test_load_environment_default_location(self, mock_load_dotenv):
        """Test environment loading with default location."""
        config = load_environment()

        self.assertEqual(config['project_id'], 'test-project')
        self.assertEqual(config['location'], 'us-central1')  # Default

    def test_is_message_id_header_valid(self):
        """Test valid Message-ID header detection."""
        valid_message_ids = [
            '684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail',
            'abc123@example.com',
            'test-message@server.local',
            '12345@mail-server.domain.co.jp'
        ]

        for message_id in valid_message_ids:
            with self.subTest(message_id=message_id):
                self.assertTrue(is_message_id_header(message_id))

    def test_is_message_id_header_invalid(self):
        """Test invalid Message-ID header detection."""
        invalid_message_ids = [
            'not-a-message-id',  # No @
            'has spaces@example.com',  # Contains spaces
            'short@x',  # Too short
            'no-domain@',  # No domain part
            '@no-local-part.com',  # No local part
            'multiple@at@signs.com',  # Multiple @ signs
            'A' * 250 + '@toolong.com',  # Too long
            'invalid@nodotordash',  # Domain has no dot or dash
            ''  # Empty string
        ]

        for invalid_id in invalid_message_ids:
            with self.subTest(invalid_id=invalid_id):
                self.assertFalse(is_message_id_header(invalid_id))

    @patch('sys.argv', ['main.py', 'test_email.txt'])
    @patch('builtins.open', mock_open(read_data="Test email content"))
    def test_get_email_input_file(self):
        """Test getting email input from file."""
        result = get_email_input()

        self.assertEqual(result, "Test email content")

    @patch('sys.argv', ['main.py', 'nonexistent.txt'])
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_get_email_input_file_not_found(self, mock_open):
        """Test handling of non-existent file input."""
        with self.assertRaises(SystemExit):
            get_email_input()

    @patch('sys.argv', ['main.py', 'Direct email text input'])
    def test_get_email_input_direct_text(self):
        """Test getting email input from direct text argument."""
        result = get_email_input()

        self.assertEqual(result, 'Direct email text input')

    @patch('sys.argv', ['main.py'])
    @patch('builtins.input', side_effect=['Line 1', 'Line 2', EOFError()])
    def test_get_email_input_interactive(self, mock_input):
        """Test interactive email input."""
        with patch('builtins.print'):  # Suppress print output
            result = get_email_input()

        self.assertEqual(result, 'Line 1\nLine 2')

    @patch('sys.argv', ['main.py'])
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    def test_get_email_input_keyboard_interrupt(self, mock_input):
        """Test handling of keyboard interrupt during interactive input."""
        with patch('builtins.print'):  # Suppress print output
            with self.assertRaises(SystemExit):
                get_email_input()

    @patch('sys.argv', ['main.py', '684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail'])
    @patch('main.fetch_email_by_message_id_header')
    @patch('builtins.print')
    def test_get_email_input_message_id_success(self, mock_print, mock_fetch):
        """Test getting email input from Message-ID header successfully."""
        mock_fetch.return_value = "Sample email content from Gmail"

        result = get_email_input()

        self.assertEqual(result, "Sample email content from Gmail")
        mock_fetch.assert_called_once_with('684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail')

    @patch('sys.argv', ['main.py', 'test@example.com'])
    @patch('main.fetch_email_by_message_id_header')
    @patch('builtins.print')
    def test_get_email_input_message_id_fetch_failure(self, mock_print, mock_fetch):
        """Test handling of Gmail fetch failure."""
        mock_fetch.side_effect = Exception("Gmail API error")

        with self.assertRaises(SystemExit):
            get_email_input()

        mock_fetch.assert_called_once_with('test@example.com')

    @patch('sys.argv', ['main.py', 'abc123@mail-server.local'])
    @patch('main.fetch_email_by_message_id_header')
    @patch('builtins.print')
    def test_get_email_input_message_id_with_suggestions(self, mock_print, mock_fetch):
        """Test Gmail fetch failure with helpful suggestions."""
        mock_fetch.side_effect = Exception("credentials not found")

        with self.assertRaises(SystemExit):
            get_email_input()

        # Check that helpful suggestions were printed
        calls = mock_print.call_args_list
        output_text = ' '.join(str(call) for call in calls)
        self.assertIn('Gmail API', output_text)
        self.assertIn('credentials', output_text)

    def test_validate_email_input_success(self):
        """Test successful email input validation."""
        email_text = "This is a valid email with enough content to pass validation checks."

        result = validate_email_input(email_text)

        self.assertEqual(result, email_text)

    def test_validate_email_input_empty(self):
        """Test validation of empty email input."""
        with self.assertRaises(ValueError) as context:
            validate_email_input("")

        self.assertIn("Email content cannot be empty", str(context.exception))

    def test_validate_email_input_too_short(self):
        """Test validation of too short email input."""
        with self.assertRaises(ValueError) as context:
            validate_email_input("Short")

        self.assertIn("Email content too short", str(context.exception))

    def test_validate_email_input_sanitization(self):
        """Test email input sanitization removes dangerous content."""
        dangerous_email = """
        <script>alert('xss')</script>
        Meeting tomorrow at 2pm in the conference room.
        javascript:void(0)
        data:text/html,<h1>test</h1>
        """

        result = validate_email_input(dangerous_email)

        # Verify dangerous content is removed
        self.assertNotIn('<script', result)
        self.assertNotIn('javascript:', result)
        self.assertNotIn('data:', result)
        # Verify legitimate content remains
        self.assertIn('Meeting tomorrow', result)

    @patch('builtins.print')
    def test_validate_email_input_length_truncation(self, mock_print):
        """Test email input length truncation."""
        long_email = "A" * 15000  # Exceeds 10000 char limit

        result = validate_email_input(long_email)

        self.assertEqual(len(result), 10000)
        mock_print.assert_called_with("⚠️  Email content truncated to 10000 characters.")

    def test_validate_extracted_data_complete(self):
        """Test validation of complete extracted data."""
        result = validate_extracted_data(self.sample_event_data)

        self.assertEqual(result, self.sample_event_data)

    def test_validate_extracted_data_missing_keys(self):
        """Test validation adds missing keys."""
        incomplete_data = {'summary': 'Test Meeting'}

        result = validate_extracted_data(incomplete_data)

        # Verify all required keys are present
        required_keys = ['summary', 'date', 'start_time', 'location']
        for key in required_keys:
            self.assertIn(key, result)

        # Verify missing keys are set to None
        self.assertIsNone(result['date'])
        self.assertIsNone(result['start_time'])
        self.assertIsNone(result['location'])

    @patch('builtins.print')
    def test_validate_extracted_data_invalid_date(self, mock_print):
        """Test validation of invalid date format."""
        invalid_data = self.sample_event_data.copy()
        invalid_data['date'] = '15/01/2024'  # Invalid format

        result = validate_extracted_data(invalid_data)

        self.assertIsNone(result['date'])
        mock_print.assert_called_with("⚠️  Invalid date format: 15/01/2024")

    @patch('builtins.print')
    def test_validate_extracted_data_invalid_time(self, mock_print):
        """Test validation of invalid time format."""
        invalid_data = self.sample_event_data.copy()
        invalid_data['start_time'] = '2:30 PM'  # Invalid format

        result = validate_extracted_data(invalid_data)

        self.assertIsNone(result['start_time'])
        mock_print.assert_called_with("⚠️  Invalid time format: 2:30 PM")

    @patch('builtins.print')
    def test_display_event_details(self, mock_print):
        """Test event details display."""
        display_event_details(self.sample_event_data)

        # Verify print was called with expected content
        calls = mock_print.call_args_list
        call_args = [str(call) for call in calls]

        # Check for key information in the output
        output_text = ' '.join(call_args)
        self.assertIn('Test Meeting', output_text)
        self.assertIn('2024-01-15', output_text)
        self.assertIn('14:30', output_text)
        self.assertIn('Conference Room A', output_text)

    @patch('builtins.print')
    def test_display_event_details_missing_data(self, mock_print):
        """Test event details display with missing data."""
        missing_data = {
            'summary': 'Test Meeting',
            'date': None,
            'start_time': None,
            'location': None
        }

        display_event_details(missing_data)

        calls = mock_print.call_args_list
        output_text = ' '.join(str(call) for call in calls)

        # Check for "Not found" messages
        self.assertIn('Not found', output_text)

    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_get_user_confirmation_yes(self, mock_print, mock_input):
        """Test user confirmation with 'yes' response."""
        result = get_user_confirmation(self.sample_event_data)

        self.assertTrue(result)

    @patch('builtins.input', return_value='n')
    @patch('builtins.print')
    def test_get_user_confirmation_no(self, mock_print, mock_input):
        """Test user confirmation with 'no' response."""
        result = get_user_confirmation(self.sample_event_data)

        self.assertFalse(result)

    @patch('builtins.input', return_value='yes')
    @patch('builtins.print')
    def test_get_user_confirmation_yes_full(self, mock_print, mock_input):
        """Test user confirmation with 'yes' full word response."""
        result = get_user_confirmation(self.sample_event_data)

        self.assertTrue(result)

    @patch('builtins.print')
    def test_get_user_confirmation_missing_critical_data(self, mock_print):
        """Test user confirmation with missing critical data."""
        result = get_user_confirmation(self.incomplete_event_data)

        self.assertFalse(result)

        # Check that missing information message was printed
        calls = mock_print.call_args_list
        output_text = ' '.join(str(call) for call in calls)
        self.assertIn('Missing critical information', output_text)
        self.assertIn('date', output_text)

    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_get_user_confirmation_keyboard_interrupt(self, mock_print, mock_input):
        """Test user confirmation handling keyboard interrupt."""
        result = get_user_confirmation(self.sample_event_data)

        self.assertFalse(result)

    @patch('main.Calendar')
    @patch('builtins.print')
    def test_create_calendar_event_success(self, mock_print, mock_calendar):
        """Test successful calendar event creation."""
        mock_logger = MagicMock()
        mock_calendar.return_value = {'id': 'event123'}  # Simulate successful creation

        result = create_calendar_event(self.sample_event_data, mock_logger)

        self.assertTrue(result)
        mock_calendar.assert_called_once_with(self.sample_event_data)
        mock_logger.info.assert_called_with("Creating Google Calendar event...")

    @patch('main.Calendar')
    @patch('builtins.print')
    def test_create_calendar_event_failure(self, mock_print, mock_calendar):
        """Test calendar event creation failure."""
        mock_logger = MagicMock()
        mock_calendar.return_value = None  # Simulate failure

        result = create_calendar_event(self.sample_event_data, mock_logger)

        self.assertFalse(result)

    @patch('main.Calendar')
    @patch('builtins.print')
    def test_create_calendar_event_exception(self, mock_print, mock_calendar):
        """Test calendar event creation with exception."""
        mock_logger = MagicMock()
        mock_calendar.side_effect = Exception("Calendar API error")

        result = create_calendar_event(self.sample_event_data, mock_logger)

        self.assertFalse(result)
        mock_logger.error.assert_called_with("Error creating calendar event: Calendar API error")

    @patch('main.Calendar')
    @patch('builtins.print')
    def test_create_calendar_event_credentials_error(self, mock_print, mock_calendar):
        """Test calendar event creation with credentials error."""
        mock_logger = MagicMock()
        mock_calendar.side_effect = Exception("credentials not found")

        result = create_calendar_event(self.sample_event_data, mock_logger)

        self.assertFalse(result)

        # Check that helpful suggestion was printed
        calls = mock_print.call_args_list
        output_text = ' '.join(str(call) for call in calls)
        self.assertIn('credentials.json', output_text)
        self.assertIn('OAuth flow', output_text)


class TestMainIntegration(unittest.TestCase):
    """Integration tests for main.py workflow components."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.valid_email = """
        Dear team,

        Please join our quarterly review meeting on March 15, 2024 at 3:00 PM.
        The meeting will be held in the Executive Conference Room, Building A.

        We'll discuss Q1 results and plan for Q2.

        Best regards,
        Sarah
        """

    def test_email_validation_workflow(self):
        """Test complete email validation workflow."""
        # Step 1: Validate input
        validated_email = validate_email_input(self.valid_email)
        self.assertIsInstance(validated_email, str)
        self.assertGreater(len(validated_email), 20)

        # Step 2: Simulate AI extraction (would normally call Vertex AI)
        mock_extracted_data = {
            'summary': 'Quarterly Review Meeting',
            'date': '2024-03-15',
            'start_time': '15:00',
            'location': 'Executive Conference Room, Building A'
        }

        # Step 3: Validate extracted data
        validated_data = validate_extracted_data(mock_extracted_data)

        # Verify all required keys are present and valid
        required_keys = ['summary', 'date', 'start_time', 'location']
        for key in required_keys:
            self.assertIn(key, validated_data)
            self.assertIsNotNone(validated_data[key])

    @patch('builtins.print')
    def test_error_handling_workflow(self, mock_print):
        """Test error handling in validation workflow."""
        # Test with invalid data
        invalid_data = {
            'summary': 'Test Meeting',
            'date': 'invalid-date',
            'start_time': 'invalid-time',
            'location': 'Conference Room'
        }

        result = validate_extracted_data(invalid_data)

        # Verify invalid data is set to None
        self.assertIsNone(result['date'])
        self.assertIsNone(result['start_time'])

        # Verify valid data is preserved
        self.assertEqual(result['summary'], 'Test Meeting')
        self.assertEqual(result['location'], 'Conference Room')


if __name__ == '__main__':
    # Configure test runner with verbose output
    unittest.main(verbosity=2)