import unittest
import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.event_parser import extract_event_details


class TestEventParserIntegration(unittest.TestCase):
    """Integration tests for event_parser module - requires real Vertex AI access."""

    @classmethod
    def setUpClass(cls):
        """Set up integration test environment."""
        # Load environment variables
        load_dotenv()

        # Get required environment variables
        cls.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        cls.location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

        # Check if required environment variables are set
        cls.has_gcp_config = bool(cls.project_id)

        if not cls.has_gcp_config:
            print("\nWarning: Google Cloud configuration not found. Integration tests will be skipped.")
            print("To run integration tests:")
            print("1. Set GOOGLE_CLOUD_PROJECT_ID in your .env file")
            print("2. Ensure you have Vertex AI authentication set up")
            print("3. Run the tests again")
        else:
            print(f"\nRunning integration tests with project: {cls.project_id}, location: {cls.location}")

    def setUp(self):
        """Set up individual test."""
        if not self.has_gcp_config:
            self.skipTest("Google Cloud configuration not available")

    def test_extract_event_details_simple_meeting(self):
        """Test event extraction with a simple meeting email."""
        email_text = """
        Hi team,

        Let's have our weekly standup meeting on January 15, 2024 at 10:00 AM.
        We'll meet in Conference Room B on the 3rd floor.

        Best regards,
        Manager
        """

        try:
            result = extract_event_details(self.project_id, self.location, email_text)

            # Verify the result is a dictionary
            self.assertIsInstance(result, dict)

            # Verify required keys are present
            required_keys = ['summary', 'date', 'start_time', 'location']
            for key in required_keys:
                self.assertIn(key, result, f"Missing key: {key}")

            # Verify data types and formats
            if result['date']:
                self.assertRegex(result['date'], r'\d{4}-\d{2}-\d{2}', "Date should be in YYYY-MM-DD format")

            if result['start_time']:
                self.assertRegex(result['start_time'], r'\d{2}:\d{2}', "Time should be in HH:MM format")

            print(f"Extracted event details: {json.dumps(result, indent=2)}")

        except Exception as e:
            self.fail(f"Event extraction failed with error: {str(e)}")

    def test_extract_event_details_complex_email(self):
        """Test event extraction with a more complex email containing multiple pieces of information."""
        email_text = """
        Dear colleagues,

        I'm writing to invite you to our quarterly business review meeting scheduled for
        March 22, 2024 at 2:30 PM. The meeting will take place at our downtown office
        located at 456 Business Ave, Suite 200, San Francisco, CA.

        We'll be discussing Q1 results and planning for Q2. Please bring your department reports.

        The meeting is expected to last approximately 2 hours.

        Looking forward to seeing everyone there.

        Sarah Johnson
        Operations Manager
        """

        try:
            result = extract_event_details(self.project_id, self.location, email_text)

            # Verify the result structure
            self.assertIsInstance(result, dict)

            # Check for expected content
            if result['summary']:
                self.assertIsInstance(result['summary'], str)
                self.assertGreater(len(result['summary']), 0)

            if result['date']:
                self.assertEqual(result['date'], '2024-03-22')

            if result['start_time']:
                self.assertEqual(result['start_time'], '14:30')

            if result['location']:
                self.assertIn('Business Ave', result['location'])

            print(f"Complex email extraction result: {json.dumps(result, indent=2)}")

        except Exception as e:
            self.fail(f"Complex email extraction failed with error: {str(e)}")

    def test_extract_event_details_incomplete_information(self):
        """Test event extraction with incomplete information."""
        email_text = """
        Team meeting next Friday. Let's discuss the project updates.
        """

        try:
            result = extract_event_details(self.project_id, self.location, email_text)

            # Verify the result structure
            self.assertIsInstance(result, dict)

            # With incomplete information, some fields should be null
            required_keys = ['summary', 'date', 'start_time', 'location']
            for key in required_keys:
                self.assertIn(key, result, f"Missing key: {key}")

            # Should have some summary since "team meeting" is mentioned
            if result['summary']:
                self.assertIsInstance(result['summary'], str)
                self.assertGreater(len(result['summary']), 0)

            print(f"Incomplete information result: {json.dumps(result, indent=2)}")

        except Exception as e:
            self.fail(f"Incomplete information extraction failed with error: {str(e)}")

    def test_extract_event_details_multiple_events(self):
        """Test event extraction with email containing multiple events (should extract the first/main one)."""
        email_text = """
        Hi everyone,

        This week we have several important meetings:

        1. Project kickoff meeting on Monday, January 8, 2024 at 9:00 AM in Room 101
        2. Client presentation on Wednesday, January 10, 2024 at 3:00 PM via Zoom
        3. Team lunch on Friday, January 12, 2024 at 12:00 PM at Mario's Restaurant

        Please mark your calendars accordingly.

        Thanks,
        Project Manager
        """

        try:
            result = extract_event_details(self.project_id, self.location, email_text)

            # Verify the result structure
            self.assertIsInstance(result, dict)

            # Should extract information from the first/primary event
            required_keys = ['summary', 'date', 'start_time', 'location']
            for key in required_keys:
                self.assertIn(key, result, f"Missing key: {key}")

            print(f"Multiple events extraction result: {json.dumps(result, indent=2)}")

        except Exception as e:
            self.fail(f"Multiple events extraction failed with error: {str(e)}")

    def test_extract_event_details_different_date_formats(self):
        """Test event extraction with different date formats."""
        email_text = """
        Please join us for the annual company picnic on July 4th, 2024 starting at 11:30 AM.
        Location: Central Park, near the main entrance.
        """

        try:
            result = extract_event_details(self.project_id, self.location, email_text)

            # Verify the result structure
            self.assertIsInstance(result, dict)

            # Check date conversion to standard format
            if result['date']:
                self.assertEqual(result['date'], '2024-07-04')

            if result['start_time']:
                self.assertEqual(result['start_time'], '11:30')

            print(f"Different date format result: {json.dumps(result, indent=2)}")

        except Exception as e:
            self.fail(f"Different date format extraction failed with error: {str(e)}")

    def test_extract_event_details_response_consistency(self):
        """Test that the same input produces consistent results."""
        email_text = """
        Department meeting scheduled for February 14, 2024 at 1:00 PM.
        Conference Room Alpha, Building A.
        """

        try:
            # Run the same extraction twice
            result1 = extract_event_details(self.project_id, self.location, email_text)
            result2 = extract_event_details(self.project_id, self.location, email_text)

            # Both results should be dictionaries
            self.assertIsInstance(result1, dict)
            self.assertIsInstance(result2, dict)

            # Key structural elements should be consistent
            self.assertEqual(set(result1.keys()), set(result2.keys()))

            # Date and time should be exactly the same if present
            if result1['date'] and result2['date']:
                self.assertEqual(result1['date'], result2['date'])

            if result1['start_time'] and result2['start_time']:
                self.assertEqual(result1['start_time'], result2['start_time'])

            print(f"Consistency test - Result 1: {json.dumps(result1, indent=2)}")
            print(f"Consistency test - Result 2: {json.dumps(result2, indent=2)}")

        except Exception as e:
            self.fail(f"Consistency test failed with error: {str(e)}")


if __name__ == '__main__':
    # Set up more verbose output for integration tests
    unittest.main(verbosity=2)