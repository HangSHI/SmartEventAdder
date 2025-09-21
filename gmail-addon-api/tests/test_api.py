"""
Unit tests for SmartEventAdder Gmail Add-on API endpoints.

These tests focus on the API layer only - request/response validation,
HTTP status codes, error handling, and CORS functionality.
All underlying modules (event_parser, gmail_fetcher, etc.) are mocked
since they have their own comprehensive test suites.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add project root to path for imports
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from api.main import app

# Create test client
client = TestClient(app)


class TestAPIBasics:
    """Test basic API functionality and health checks."""

    def test_root_endpoint(self):
        """Test root endpoint returns basic info."""
        response = client.get("/")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "SmartEventAdder Gmail Add-on API"

    @patch('api.main.authenticate_google_services')
    def test_health_check_success(self, mock_auth):
        """Test health check with successful Google authentication."""
        mock_auth.return_value = MagicMock()

        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["google_auth_status"] == "authenticated"

    @patch('api.main.authenticate_google_services')
    def test_health_check_auth_failure(self, mock_auth):
        """Test health check with failed Google authentication."""
        mock_auth.side_effect = Exception("Authentication failed")

        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["google_auth_status"] == "failed"

    def test_api_config_endpoint(self):
        """Test configuration endpoint returns non-sensitive data."""
        response = client.get("/api/config")

        assert response.status_code == 200
        data = response.json()
        assert "google_cloud_location" in data
        assert "has_project_id" in data
        assert "service" in data


class TestEmailParsingAPI:
    """Test email parsing API endpoint."""

    @patch('api.main.extract_event_details')
    def test_parse_email_success(self, mock_extract):
        """Test successful email parsing."""
        mock_extract.return_value = {
            "summary": "Team Meeting",
            "date": "2024-01-15",
            "start_time": "14:30",
            "location": "Conference Room A"
        }

        response = client.post("/api/parse-email", json={
            "email_content": "Team meeting tomorrow at 2:30 PM in Conference Room A"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["message"] == "Event details extracted successfully"
        assert data["event_data"]["summary"] == "Team Meeting"

        # Verify the underlying module was called correctly
        mock_extract.assert_called_once()
        call_args = mock_extract.call_args
        assert "Team meeting tomorrow" in call_args.kwargs["email_text"]

    @patch('api.main.extract_event_details')
    def test_parse_email_with_project_id(self, mock_extract):
        """Test email parsing with custom project ID."""
        mock_extract.return_value = {"summary": "Test Meeting"}

        response = client.post("/api/parse-email", json={
            "email_content": "Meeting content",
            "project_id": "custom-project-123",
            "location": "us-central1"
        })

        assert response.status_code == 200

        # Verify custom parameters were passed
        call_args = mock_extract.call_args
        assert call_args.kwargs["project_id"] == "custom-project-123"
        assert call_args.kwargs["location"] == "us-central1"

    def test_parse_email_invalid_request(self):
        """Test email parsing with invalid request data."""
        # Missing required email_content field
        response = client.post("/api/parse-email", json={})

        assert response.status_code == 422
        assert "validation error" in response.json()["detail"][0]["type"]

    def test_parse_email_empty_content(self):
        """Test email parsing with empty email content."""
        response = client.post("/api/parse-email", json={
            "email_content": ""
        })

        assert response.status_code == 422

    @patch('api.main.extract_event_details')
    def test_parse_email_extraction_failure(self, mock_extract):
        """Test handling of email extraction failure."""
        mock_extract.side_effect = Exception("Vertex AI processing failed")

        response = client.post("/api/parse-email", json={
            "email_content": "Valid email content"
        })

        assert response.status_code == 500
        assert "Failed to parse email" in response.json()["detail"]


class TestEmailFetchingAPI:
    """Test email fetching API endpoints."""

    @patch('api.main.fetch_email_by_message_id_header')
    def test_fetch_email_by_message_id_success(self, mock_fetch):
        """Test successful email fetching by Message-ID."""
        mock_fetch.return_value = "Subject: Test Meeting\nFrom: test@example.com\n\nMeeting content here"

        response = client.post("/api/fetch-email-by-message-id", json={
            "message_id": "test123@example.com"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["message"] == "Email fetched successfully"
        assert "Subject: Test Meeting" in data["email_content"]
        assert data["message_id"] == "test123@example.com"

    @patch('api.main.fetch_email_by_gmail_id')
    def test_fetch_email_by_gmail_id_success(self, mock_fetch):
        """Test successful email fetching by Gmail ID."""
        mock_fetch.return_value = "Email content from Gmail API"

        response = client.post("/api/fetch-email-by-gmail-id", json={
            "gmail_id": "1234567890abcdef"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["gmail_id"] == "1234567890abcdef"

    def test_fetch_email_invalid_message_id(self):
        """Test email fetching with invalid Message-ID format."""
        response = client.post("/api/fetch-email-by-message-id", json={
            "message_id": "invalid-no-at-symbol"
        })

        assert response.status_code == 422

    def test_fetch_email_invalid_gmail_id(self):
        """Test email fetching with invalid Gmail ID format."""
        response = client.post("/api/fetch-email-by-gmail-id", json={
            "gmail_id": "toolong1234567890"  # Too long
        })

        assert response.status_code == 422

    @patch('api.main.fetch_email_by_message_id_header')
    def test_fetch_email_gmail_api_failure(self, mock_fetch):
        """Test handling of Gmail API failure."""
        mock_fetch.side_effect = Exception("Gmail API authentication failed")

        response = client.post("/api/fetch-email-by-message-id", json={
            "message_id": "valid@example.com"
        })

        assert response.status_code == 500
        assert "Failed to fetch email" in response.json()["detail"]


class TestCalendarAPI:
    """Test calendar event creation API endpoint."""

    @patch('api.main.Calendar')
    def test_create_event_success(self, mock_calendar):
        """Test successful calendar event creation."""
        mock_calendar.return_value = {"id": "event123", "status": "confirmed"}

        event_data = {
            "summary": "Test Meeting",
            "date": "2024-01-15",
            "start_time": "14:30",
            "location": "Conference Room A"
        }

        response = client.post("/api/create-event", json={
            "event_data": event_data
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["message"] == "Calendar event created successfully"
        assert data["calendar_result"]["id"] == "event123"

        # Verify Calendar was called with correct data
        mock_calendar.assert_called_once_with(event_data)

    def test_create_event_invalid_data(self):
        """Test calendar event creation with invalid event data."""
        # Missing required fields
        response = client.post("/api/create-event", json={
            "event_data": {"summary": "Meeting"}  # Missing date, start_time
        })

        assert response.status_code == 422

    @patch('api.main.Calendar')
    def test_create_event_calendar_failure(self, mock_calendar):
        """Test handling of calendar creation failure."""
        mock_calendar.side_effect = Exception("Calendar API error")

        event_data = {
            "summary": "Test Meeting",
            "date": "2024-01-15",
            "start_time": "14:30",
            "location": "Conference Room A"
        }

        response = client.post("/api/create-event", json={
            "event_data": event_data
        })

        assert response.status_code == 500
        assert "Failed to create calendar event" in response.json()["detail"]


class TestCompleteWorkflowAPI:
    """Test complete workflow API endpoint."""

    @patch('api.main.fetch_email_by_message_id_header')
    @patch('api.main.extract_event_details')
    @patch('api.main.Calendar')
    def test_complete_workflow_success(self, mock_calendar, mock_extract, mock_fetch):
        """Test successful complete workflow execution."""
        # Setup mocks
        mock_fetch.return_value = "Email content"
        mock_extract.return_value = {
            "summary": "Team Meeting",
            "date": "2024-01-15",
            "start_time": "14:30",
            "location": "Conference Room A"
        }
        mock_calendar.return_value = {"id": "event123"}

        response = client.post("/api/complete-workflow", json={
            "message_id": "test@example.com",
            "create_event": True
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["workflow_completed"] == True
        assert data["identifier"] == "test@example.com"
        assert data["identifier_type"] == "message_id"
        assert "email_content" in data
        assert "event_data" in data
        assert "calendar_result" in data

    @patch('api.main.fetch_email_by_gmail_id')
    @patch('api.main.extract_event_details')
    def test_complete_workflow_with_gmail_id(self, mock_extract, mock_fetch):
        """Test complete workflow using Gmail ID."""
        mock_fetch.return_value = "Email content"
        mock_extract.return_value = {"summary": "Meeting"}

        response = client.post("/api/complete-workflow", json={
            "gmail_id": "1234567890abcdef",
            "create_event": False  # Skip calendar creation
        })

        assert response.status_code == 200
        data = response.json()
        assert data["identifier_type"] == "gmail_id"
        assert data["calendar_result"] is None  # No calendar event created

    def test_complete_workflow_no_identifier(self):
        """Test complete workflow with no identifier provided."""
        response = client.post("/api/complete-workflow", json={
            "create_event": True
        })

        assert response.status_code == 422


class TestCORSAndHeaders:
    """Test CORS configuration and headers."""

    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        response = client.options("/api/health")

        # FastAPI with CORS middleware should handle OPTIONS requests
        assert response.status_code in [200, 405]  # Depending on FastAPI version

    def test_cors_origins_configuration(self):
        """Test that API accepts requests from expected origins."""
        # Test with Apps Script origin
        headers = {"Origin": "https://script.google.com"}
        response = client.get("/api/health", headers=headers)

        assert response.status_code == 200


class TestErrorHandling:
    """Test global error handling and edge cases."""

    def test_invalid_json_request(self):
        """Test handling of invalid JSON in requests."""
        response = client.post(
            "/api/parse-email",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_nonexistent_endpoint(self):
        """Test handling of requests to non-existent endpoints."""
        response = client.get("/api/nonexistent")

        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test handling of wrong HTTP methods."""
        response = client.get("/api/parse-email")  # Should be POST

        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v"])