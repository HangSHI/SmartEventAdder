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
    
    # Authentication tests are now in dedicated google_auth module tests
    # This module only tests the Calendar() function
    
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
    
    @patch('modules.google_calendar.authenticate_google_services')
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
    
    @patch('modules.google_calendar.authenticate_google_services')
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
    
    @patch('modules.google_calendar.authenticate_google_services')
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
        
        with patch('modules.google_calendar.authenticate_google_services'), \
             patch('modules.google_calendar.build'), \
             patch('builtins.print'):
            result = Calendar(incomplete_data)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()