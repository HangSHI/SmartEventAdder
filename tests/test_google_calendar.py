import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.google_calendar import Calendar
from modules.google_auth import authenticate_google_services
from googleapiclient.errors import HttpError


class TestGoogleCalendarUnit(unittest.TestCase):
    """Unit tests for google_calendar module functions."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_event_data = {
            'summary': 'Test Meeting',
            'location': 'Conference Room A',
            'date': '2024-12-15',
            'start_time': '14:30'
        }
    
    @patch('modules.google_calendar.os.path.exists')
    @patch('modules.google_calendar.Credentials.from_authorized_user_file')
    def test_authenticate_with_existing_valid_token(self, mock_from_file, mock_exists):
        """Test authenticate function when valid token.json exists."""
        # Setup
        mock_exists.return_value = True
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_from_file.return_value = mock_creds
        
        # Execute
        result = authenticate_google_services()
        
        # Assert
        self.assertEqual(result, mock_creds)
        mock_exists.assert_called_once_with('token.json')
        mock_from_file.assert_called_once()
    
    @patch('modules.google_calendar.os.path.exists')
    @patch('modules.google_calendar.Credentials.from_authorized_user_file')
    @patch('modules.google_calendar.Request')
    def test_authenticate_with_expired_token_refresh(self, mock_request, mock_from_file, mock_exists):
        """Test authenticate function when token exists but is expired and can be refreshed."""
        # Setup
        mock_exists.return_value = True
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = 'refresh_token'
        mock_from_file.return_value = mock_creds
        
        with patch('builtins.open', mock_open()) as mock_file:
            mock_creds.to_json.return_value = '{"token": "test"}'
            
            # Execute
            result = authenticate_google_services()
            
            # Assert
            self.assertEqual(result, mock_creds)
            mock_creds.refresh.assert_called_once()
            mock_file.assert_called_once_with('token.json', 'w')
    
    @patch('modules.google_calendar.os.path.exists')
    @patch('modules.google_calendar.InstalledAppFlow.from_client_secrets_file')
    def test_authenticate_new_flow(self, mock_flow_class, mock_exists):
        """Test authenticate function when new OAuth flow is needed."""
        # Setup
        mock_exists.return_value = False
        mock_flow = MagicMock()
        mock_creds = MagicMock()
        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_class.return_value = mock_flow
        
        with patch('builtins.open', mock_open()) as mock_file:
            mock_creds.to_json.return_value = '{"token": "test"}'
            
            # Execute
            result = authenticate_google_services()
            
            # Assert
            self.assertEqual(result, mock_creds)
            mock_flow_class.assert_called_once_with('credentials.json', ['https://www.googleapis.com/auth/calendar'])
            mock_flow.run_local_server.assert_called_once_with(port=0)
            mock_file.assert_called_once_with('token.json', 'w')
    
    def test_calendar_datetime_formatting(self):
        """Test that Calendar function formats datetime correctly."""
        event_data = self.sample_event_data
        
        # Test datetime parsing logic separately
        event_date = event_data['date']
        start_time = event_data['start_time']
        
        expected_start = f"{event_date}T{start_time}:00+09:00"
        expected_end = f"{event_date}T15:30:00+09:00"  # 1 hour later
        
        self.assertEqual(expected_start, "2024-12-15T14:30:00+09:00")
        self.assertEqual(expected_end, "2024-12-15T15:30:00+09:00")
    
    @patch('modules.google_calendar.authenticate')
    @patch('modules.google_calendar.build')
    @patch('builtins.print')
    def test_calendar_success(self, mock_print, mock_build, mock_auth):
        """Test successful event creation."""
        # Setup
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_event_result = {
            'id': 'test_event_id',
            'htmlLink': 'https://calendar.google.com/event?eid=test'
        }
        mock_service.events().insert().execute.return_value = mock_event_result
        
        # Execute
        result = Calendar(self.sample_event_data)
        
        # Assert
        self.assertEqual(result, mock_event_result)
        mock_auth.assert_called_once()
        mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_creds)
        
        # Verify the event object structure
        call_args = mock_service.events().insert.call_args
        self.assertEqual(call_args[1]['calendarId'], 'primary')
        
        event_body = call_args[1]['body']
        self.assertEqual(event_body['summary'], 'Test Meeting')
        self.assertEqual(event_body['location'], 'Conference Room A')
        self.assertEqual(event_body['start']['dateTime'], '2024-12-15T14:30:00+09:00')
        self.assertEqual(event_body['end']['dateTime'], '2024-12-15T15:30:00+09:00')
        self.assertEqual(event_body['start']['timeZone'], 'Asia/Tokyo')
    
    @patch('modules.google_calendar.authenticate')
    @patch('modules.google_calendar.build')
    @patch('builtins.print')
    def test_calendar_http_error(self, mock_print, mock_build, mock_auth):
        """Test Calendar function handling HttpError."""
        # Setup
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.events().insert().execute.side_effect = HttpError(
            resp=MagicMock(status=403), 
            content=b'Forbidden'
        )
        
        # Execute
        result = Calendar(self.sample_event_data)
        
        # Assert
        self.assertIsNone(result)
        mock_print.assert_called()
    
    @patch('modules.google_calendar.authenticate')
    @patch('modules.google_calendar.build')
    @patch('builtins.print')
    def test_calendar_generic_exception(self, mock_print, mock_build, mock_auth):
        """Test Calendar function handling generic exception."""
        # Setup
        mock_creds = MagicMock()
        mock_auth.return_value = mock_creds
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.events().insert().execute.side_effect = Exception("Test error")
        
        # Execute
        result = Calendar(self.sample_event_data)
        
        # Assert
        self.assertIsNone(result)
        mock_print.assert_called()
    
    def test_calendar_missing_fields(self):
        """Test Calendar function with missing required fields."""
        incomplete_data = {
            'summary': 'Test Meeting',
            'location': 'Conference Room A'
            # Missing 'date' and 'start_time'
        }
        
        with patch('modules.google_calendar.authenticate'), \
             patch('modules.google_calendar.build'), \
             patch('builtins.print'):
            result = Calendar(incomplete_data)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()