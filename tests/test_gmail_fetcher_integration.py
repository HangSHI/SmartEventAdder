import unittest
import os
import sys
from unittest import skip

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.gmail_fetcher import (
    fetch_email_by_id,
    fetch_email_by_url,
    extract_message_id_from_url,
    validate_message_id,
    authenticate_gmail
)


class TestGmailFetcherIntegration(unittest.TestCase):
    """
    Integration tests for gmail_fetcher module with real Gmail API.

    REQUIREMENTS:
    1. Valid Gmail API credentials (credentials.json)
    2. Completed OAuth2 authentication (token.json)
    3. Gmail API enabled in Google Cloud Console
    4. Real Gmail message IDs or URLs for testing

    SETUP:
    - Run: ./setup_gcloud.sh
    - Ensure Gmail API is enabled
    - Delete token.json to re-authenticate with Gmail permissions
    """

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures for integration tests."""
        # Check if credentials exist
        cls.has_credentials = os.path.exists('credentials.json')
        cls.has_environment = os.path.exists('.env')

        # Test Gmail URLs and Message IDs will be set by individual tests
        cls.test_gmail_urls = []
        cls.test_message_ids = []

        # Skip integration tests if no credentials
        if not cls.has_credentials:
            cls.skip_reason = "Missing credentials.json file. Run ./setup_gcloud.sh first."
        elif not cls.has_environment:
            cls.skip_reason = "Missing .env file. Check project setup."
        else:
            cls.skip_reason = None

    def setUp(self):
        """Set up test fixtures before each test method."""
        if self.skip_reason:
            self.skipTest(self.skip_reason)

    def test_authenticate_gmail_integration(self):
        """Test Gmail authentication with real credentials."""
        try:
            creds = authenticate_gmail()
            self.assertIsNotNone(creds)
            self.assertTrue(creds.valid)
            print(f"✅ Gmail authentication successful")
        except Exception as e:
            self.fail(f"Gmail authentication failed: {str(e)}")

    def test_extract_message_id_from_real_url(self):
        """Test extracting message ID from real Gmail URLs."""
        # Test cases with real Gmail URLs
        test_cases = [
            ("https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr", "FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr"),
            ("https://mail.google.com/mail/u/0/#search/予約/FMfcgzQbgcQTZvmQLHXPxgKmCvJZFGKp", "FMfcgzQbgcQTZvmQLHXPxgKmCvJZFGKp"),
            ("https://mail.google.com/mail/u/0/#search/予約/FMfcgzQbfnxmdnbjNwSnLThtCtPmmfDz", "FMfcgzQbfnxmdnbjNwSnLThtCtPmmfDz"),
        ]

        if not test_cases:
            self.skipTest("No real Gmail URLs provided for testing. Add URLs to test_cases list.")

        for gmail_url, expected_id in test_cases:
            with self.subTest(url=gmail_url):
                extracted_id = extract_message_id_from_url(gmail_url)
                self.assertEqual(extracted_id, expected_id)
                self.assertTrue(validate_message_id(extracted_id))
                print(f"✅ Extracted ID from URL: {extracted_id}")

    def test_fetch_email_by_real_message_id(self):
        """Test fetching real emails by message ID."""
        # Test message IDs - real Gmail message IDs
        test_message_ids = [
            "FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr",
            "FMfcgzQbgcQTZvmQLHXPxgKmCvJZFGKp",
            "FMfcgzQbfnxmdnbjNwSnLThtCtPmmfDz",
        ]

        if not test_message_ids:
            self.skipTest("No real Gmail message IDs provided for testing. Add IDs to test_message_ids list.")

        for message_id in test_message_ids:
            with self.subTest(message_id=message_id):
                try:
                    # Validate message ID format first
                    self.assertTrue(validate_message_id(message_id),
                                  f"Invalid message ID format: {message_id}")

                    # Fetch the email
                    email_content = fetch_email_by_id(message_id)

                    # Basic validation of fetched content
                    self.assertIsInstance(email_content, str)
                    self.assertGreater(len(email_content), 0)
                    self.assertIn("Subject:", email_content)

                    # Print first 200 characters for verification
                    print(f"✅ Fetched email {message_id}:")
                    print(f"   Content preview: {email_content[:200]}...")

                except Exception as e:
                    self.fail(f"Failed to fetch email {message_id}: {str(e)}")

    def test_fetch_email_from_real_gmail_url(self):
        """Test complete workflow: Gmail URL -> Email Content using fetch_email_by_url()."""
        # Real Gmail URLs for testing
        test_gmail_urls = [
            "https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr",
            "https://mail.google.com/mail/u/0/#search/予約/FMfcgzQbgcQTZvmQLHXPxgKmCvJZFGKp",
            "https://mail.google.com/mail/u/0/#search/予約/FMfcgzQbfnxmdnbjNwSnLThtCtPmmfDz",
        ]

        if not test_gmail_urls:
            self.skipTest("No real Gmail URLs provided for testing. Add URLs to test_gmail_urls list.")

        for gmail_url in test_gmail_urls:
            with self.subTest(url=gmail_url):
                try:
                    # Use the complete Gmail URL workflow
                    email_content = fetch_email_by_url(gmail_url)

                    # Validate results
                    self.assertIsInstance(email_content, str)
                    self.assertGreater(len(email_content), 0)
                    self.assertIn("Subject:", email_content)

                    print(f"✅ Complete workflow successful for URL: {gmail_url}")
                    print(f"   Email preview: {email_content[:150]}...")

                except Exception as e:
                    self.fail(f"Complete workflow failed for {gmail_url}: {str(e)}")

    def test_fetch_nonexistent_message_id(self):
        """Test fetching with a nonexistent but valid-format message ID."""
        # Use a valid format but nonexistent message ID
        fake_message_id = "1234567890abcdef"

        with self.assertRaises(Exception) as context:
            fetch_email_by_id(fake_message_id)

        # Should get a "not found" error
        self.assertIn("not found", str(context.exception).lower())
        print(f"✅ Correctly handled nonexistent message ID: {fake_message_id}")

    def test_authentication_permissions(self):
        """Test that authentication includes proper Gmail permissions."""
        try:
            creds = authenticate_gmail()

            # Check if scopes include Gmail
            if hasattr(creds, 'scopes'):
                scopes = creds.scopes
                gmail_scope_found = any('gmail' in scope for scope in scopes)
                self.assertTrue(gmail_scope_found,
                              "Gmail scope not found in credentials. Re-authenticate with updated scopes.")
                print(f"✅ Gmail permissions verified in scopes")
            else:
                print("⚠️  Cannot verify scopes directly, but authentication succeeded")

        except Exception as e:
            self.fail(f"Authentication permission test failed: {str(e)}")


class TestGmailFetcherRealWorldScenarios(unittest.TestCase):
    """
    Real-world scenario tests for Gmail fetcher integration.

    These tests simulate actual usage patterns and edge cases.
    """

    def setUp(self):
        """Set up test fixtures."""
        # Skip if no credentials
        if not os.path.exists('credentials.json'):
            self.skipTest("Missing credentials.json file")

    def test_html_email_extraction(self):
        """Test extraction of HTML emails (common in real Gmail)."""
        # This would test with a real HTML email message ID
        # Commented out until real message ID is provided
        pass

    def test_multipart_email_extraction(self):
        """Test extraction of multipart emails with attachments."""
        # This would test with a real multipart email message ID
        # Commented out until real message ID is provided
        pass

    def test_email_with_special_characters(self):
        """Test emails with special characters, emojis, etc."""
        # This would test with a real email containing special characters
        # Commented out until real message ID is provided
        pass


def add_test_gmail_urls(urls):
    """
    Helper function to add Gmail URLs for testing.

    Usage:
        from tests.test_gmail_fetcher_integration import add_test_gmail_urls
        add_test_gmail_urls([
            "https://mail.google.com/mail/u/0/#inbox/your_message_id_1",
            "https://mail.google.com/mail/u/0/#inbox/your_message_id_2"
        ])
    """
    TestGmailFetcherIntegration.test_gmail_urls.extend(urls)


def add_test_message_ids(message_ids):
    """
    Helper function to add message IDs for testing.

    Usage:
        from tests.test_gmail_fetcher_integration import add_test_message_ids
        add_test_message_ids([
            "your_message_id_1",
            "your_message_id_2"
        ])
    """
    TestGmailFetcherIntegration.test_message_ids.extend(message_ids)


if __name__ == '__main__':
    # Instructions for running integration tests
    print("="*60)
    print("Gmail Fetcher Integration Tests")
    print("="*60)
    print("SETUP REQUIRED:")
    print("1. Valid credentials.json file")
    print("2. Gmail API enabled in Google Cloud Console")
    print("3. OAuth2 authentication completed")
    print("4. Real Gmail URLs or message IDs for testing")
    print("")
    print("TO ADD TEST DATA:")
    print("Edit this file and add real Gmail URLs/message IDs to:")
    print("- test_extract_message_id_from_real_url()")
    print("- test_fetch_email_by_real_message_id()")
    print("- test_fetch_email_from_real_gmail_url()")
    print("="*60)
    print("")

    unittest.main(verbosity=2)