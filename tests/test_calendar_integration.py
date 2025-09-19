import unittest
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.google_calendar import Calendar
from modules.google_auth import authenticate_google_services


class TestGoogleCalendarIntegration(unittest.TestCase):
    """Integration tests for google_calendar module - requires real API credentials."""
    
    @classmethod
    def setUpClass(cls):
        """Set up integration test environment."""
        # Load environment variables
        load_dotenv()
        
        # Check if credentials files exist
        cls.has_credentials = os.path.exists('credentials.json')
        cls.has_token = os.path.exists('token.json')
        
        if not cls.has_credentials:
            print("\nWarning: credentials.json not found. Integration tests will be skipped.")
            print("To run integration tests:")
            print("1. Place your Google Calendar API credentials.json file in the project root")
            print("2. Run the tests again")
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        if not self.has_credentials:
            self.skipTest("credentials.json not found - skipping integration test")
        
        # Create test event data with current date + 1 day to avoid conflicts
        tomorrow = datetime.now() + timedelta(days=1)
        self.test_event_data = {
            'summary': f'Integration Test Event - {datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'location': 'Test Location - Integration Test',
            'date': tomorrow.strftime('%Y-%m-%d'),
            'start_time': '15:30'
        }
    
    def test_authenticate_integration(self):
        """Test authentication with real credentials."""
        try:
            creds = authenticate_google_services()
            self.assertIsNotNone(creds)
            self.assertTrue(creds.valid)
            print(f"✓ Authentication successful")
        except Exception as e:
            self.fail(f"Authentication failed: {e}")
    
    def test_calendar_create_event_integration(self):
        """Test creating a real event on Google Calendar."""
        try:
            result = Calendar(self.test_event_data)
            
            # Verify event was created
            self.assertIsNotNone(result)
            self.assertIn('id', result)
            self.assertIn('htmlLink', result)
            
            print(f"✓ Event created successfully:")
            print(f"  Event ID: {result.get('id')}")
            print(f"  Event Link: {result.get('htmlLink')}")
            print(f"  Summary: {self.test_event_data['summary']}")
            print(f"  Date: {self.test_event_data['date']} at {self.test_event_data['start_time']} JST")
            
        except Exception as e:
            self.fail(f"Event creation failed: {e}")
    
    def test_calendar_with_special_characters(self):
        """Test creating an event with special characters."""
        special_event_data = {
            'summary': 'Test Event with Special Characters: åäö éñü 日本語 🎉',
            'location': 'Location with symbols: @#$%^&*()',
            'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'start_time': '16:45'
        }
        
        try:
            result = Calendar(special_event_data)
            
            self.assertIsNotNone(result)
            self.assertIn('id', result)
            print(f"✓ Event with special characters created successfully")
            
        except Exception as e:
            self.fail(f"Event creation with special characters failed: {e}")
    
    def test_calendar_edge_times(self):
        """Test creating events at edge times (early morning, late night)."""
        edge_cases = [
            {
                'summary': 'Early Morning Meeting - Integration Test',
                'location': 'Early Bird Location',
                'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'start_time': '06:00'
            },
            {
                'summary': 'Late Night Meeting - Integration Test',
                'location': 'Night Owl Location',
                'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'start_time': '23:30'
            }
        ]
        
        for event_data in edge_cases:
            with self.subTest(event=event_data['summary']):
                try:
                    result = Calendar(event_data)
                    self.assertIsNotNone(result)
                    print(f"✓ Edge time event created: {event_data['start_time']}")
                except Exception as e:
                    self.fail(f"Edge time event creation failed: {e}")


class TestGoogleCalendarIntegrationManual(unittest.TestCase):
    """Manual integration tests that require user interaction."""
    
    def setUp(self):
        """Check if credentials exist."""
        if not os.path.exists('credentials.json'):
            self.skipTest("credentials.json not found - skipping manual integration test")
    
    @unittest.skip("Run manually when you want to test OAuth flow")
    def test_oauth_flow_manual(self):
        """Manual test for OAuth flow - requires user interaction."""
        # Remove token.json to force new OAuth flow
        if os.path.exists('token.json'):
            os.remove('token.json')
        
        print("\n" + "="*50)
        print("MANUAL TEST: OAuth Flow")
        print("This test will open a browser for authentication.")
        print("Please complete the OAuth flow in your browser.")
        print("="*50)
        
        try:
            creds = authenticate_google_services()
            self.assertIsNotNone(creds)
            self.assertTrue(creds.valid)
            print("✓ OAuth flow completed successfully")
        except Exception as e:
            self.fail(f"OAuth flow failed: {e}")


if __name__ == '__main__':
    # Create a custom test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add integration tests
    suite.addTests(loader.loadTestsFromTestCase(TestGoogleCalendarIntegration))
    
    # Add manual tests (they will be skipped by default)
    suite.addTests(loader.loadTestsFromTestCase(TestGoogleCalendarIntegrationManual))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print(f"\n✅ All integration tests passed!")
    else:
        print(f"\n❌ Some integration tests failed.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")