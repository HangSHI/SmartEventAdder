import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.event_parser import extract_event_details


class TestEventParser(unittest.TestCase):
    """Unit tests for event_parser module with mocked AI Platform calls."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_id = "test-project"
        self.location = "us-central1"
        self.sample_email = """
        Dear Team,

        Please join us for our monthly team meeting on January 15, 2024 at 2:30 PM.
        The meeting will be held at Conference Room A, 123 Main Street, New York, NY.

        Best regards,
        Manager
        """

        self.expected_response = {
            "summary": "Monthly team meeting",
            "date": "2024-01-15",
            "start_time": "14:30",
            "location": "Conference Room A, 123 Main Street, New York, NY"
        }

    @patch('modules.event_parser.authenticate_google_services')
    @patch('modules.event_parser.vertexai')
    @patch('modules.event_parser.GenerativeModel')
    def test_extract_event_details_success(self, mock_generative_model, mock_vertexai, mock_auth):
        """Test successful event detail extraction."""
        # Mock OAuth2 credentials
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds

        # Mock Vertex AI initialization
        mock_vertexai.init.return_value = None

        # Mock the GenerativeModel and its response
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model

        # Mock the response from the model
        mock_response = MagicMock()
        mock_response.text = json.dumps(self.expected_response)
        mock_model.generate_content.return_value = mock_response

        # Call the function
        result = extract_event_details(self.project_id, self.location, self.sample_email)

        # Verify the mocks were called correctly
        mock_auth.assert_called_once()
        mock_vertexai.init.assert_called_once_with(project=self.project_id, location=self.location, credentials=mock_creds)
        mock_generative_model.assert_called_once_with("gemini-2.0-flash-lite")
        mock_model.generate_content.assert_called_once()

        # Verify the result
        self.assertEqual(result, self.expected_response)

    @patch('modules.event_parser.authenticate_google_services')
    @patch('modules.event_parser.vertexai')
    @patch('modules.event_parser.GenerativeModel')
    def test_extract_event_details_with_null_values(self, mock_generative_model, mock_vertexai, mock_auth):
        """Test event detail extraction with missing information."""
        # Mock OAuth2 credentials
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds

        # Mock Vertex AI initialization
        mock_vertexai.init.return_value = None

        # Mock the GenerativeModel and its response
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model

        # Response with null values for missing information
        response_with_nulls = {
            "summary": "Team discussion",
            "date": None,
            "start_time": None,
            "location": "Office Building"
        }

        mock_response = MagicMock()
        mock_response.text = json.dumps(response_with_nulls)
        mock_model.generate_content.return_value = mock_response

        # Call the function
        result = extract_event_details(self.project_id, self.location, "Vague email content")

        # Verify the result includes null values
        self.assertEqual(result["summary"], "Team discussion")
        self.assertIsNone(result["date"])
        self.assertIsNone(result["start_time"])
        self.assertEqual(result["location"], "Office Building")

    @patch('modules.event_parser.authenticate_google_services')
    @patch('modules.event_parser.vertexai')
    @patch('modules.event_parser.GenerativeModel')
    def test_extract_event_details_json_parse_error(self, mock_generative_model, mock_vertexai, mock_auth):
        """Test handling of invalid JSON response."""
        # Mock OAuth2 credentials
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds

        # Mock Vertex AI initialization
        mock_vertexai.init.return_value = None

        # Mock the GenerativeModel and its response
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model

        # Mock an invalid JSON response
        mock_response = MagicMock()
        mock_response.text = "Invalid JSON response"
        mock_model.generate_content.return_value = mock_response

        # Call the function and expect a JSON decode error
        with self.assertRaises(json.JSONDecodeError):
            extract_event_details(self.project_id, self.location, self.sample_email)

    @patch('modules.event_parser.authenticate_google_services')
    @patch('modules.event_parser.vertexai')
    @patch('modules.event_parser.GenerativeModel')
    def test_extract_event_details_with_whitespace(self, mock_generative_model, mock_vertexai, mock_auth):
        """Test event detail extraction with response containing whitespace."""
        # Mock OAuth2 credentials
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds

        # Mock Vertex AI initialization
        mock_vertexai.init.return_value = None

        # Mock the GenerativeModel and its response
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model

        # Mock response with whitespace
        mock_response = MagicMock()
        mock_response.text = f"  {json.dumps(self.expected_response)}  \n"
        mock_model.generate_content.return_value = mock_response

        # Call the function
        result = extract_event_details(self.project_id, self.location, self.sample_email)

        # Verify the result (whitespace should be stripped)
        self.assertEqual(result, self.expected_response)

    @patch('modules.event_parser.authenticate_google_services')
    @patch('modules.event_parser.vertexai')
    @patch('modules.event_parser.GenerativeModel')
    def test_prompt_content(self, mock_generative_model, mock_vertexai, mock_auth):
        """Test that the prompt contains expected content."""
        # Mock OAuth2 credentials
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds

        # Mock Vertex AI initialization
        mock_vertexai.init.return_value = None

        # Mock the GenerativeModel and its response
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model

        mock_response = MagicMock()
        mock_response.text = json.dumps(self.expected_response)
        mock_model.generate_content.return_value = mock_response

        # Call the function
        extract_event_details(self.project_id, self.location, self.sample_email)

        # Get the prompt that was passed to generate_content
        call_args = mock_model.generate_content.call_args[0][0]

        # Verify the prompt contains expected elements
        self.assertIn("Extract the following event details", call_args)
        self.assertIn("summary", call_args)
        self.assertIn("date", call_args)
        self.assertIn("start_time", call_args)
        self.assertIn("location", call_args)
        self.assertIn("YYYY-MM-DD", call_args)
        self.assertIn("HH:MM", call_args)
        self.assertIn("JSON object", call_args)
        self.assertIn(self.sample_email, call_args)

    def test_function_parameters(self):
        """Test that the function has the expected parameters."""
        import inspect

        # Get function signature
        sig = inspect.signature(extract_event_details)
        params = list(sig.parameters.keys())

        # Verify expected parameters
        expected_params = ['project_id', 'location', 'email_text']
        self.assertEqual(params, expected_params)


if __name__ == '__main__':
    unittest.main()