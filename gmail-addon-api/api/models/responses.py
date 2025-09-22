"""
Response models for SmartEventAdder Gmail Add-on API.

These Pydantic models define the structure of API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union


class ApiResponse(BaseModel):
    """Base response model for all API endpoints."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: Optional[str] = Field(None, description="Human-readable message")


class HealthResponse(ApiResponse):
    """Response model for health check endpoints."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    google_auth_status: Optional[str] = Field(None, description="Google authentication status")
    details: Optional[str] = Field(None, description="Additional details")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "status": "healthy",
                "service": "SmartEventAdder Gmail Add-on API",
                "version": "1.0.0",
                "google_auth_status": "authenticated"
            }
        }


class ParseEmailResponse(ApiResponse):
    """Response model for email parsing endpoint."""
    event_data: Optional[Dict[str, Any]] = Field(None, description="Extracted event data")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Event details extracted successfully",
                "event_data": {
                    "summary": "Team Meeting",
                    "date": "2024-01-15",
                    "start_time": "14:30",
                    "location": "Conference Room A"
                }
            }
        }


class FetchEmailResponse(ApiResponse):
    """Response model for email fetching endpoints."""
    email_content: Optional[str] = Field(None, description="Fetched email content")
    message_id: Optional[str] = Field(None, description="Email Message-ID header used")
    gmail_id: Optional[str] = Field(None, description="Gmail API message ID used")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Email fetched successfully",
                "email_content": "Subject: Team Meeting\nFrom: manager@company.com\n\nPlease join our team meeting...",
                "message_id": "684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail"
            }
        }


class CreateEventResponse(ApiResponse):
    """Response model for calendar event creation endpoint."""
    calendar_result: Optional[Union[Dict[str, Any], str]] = Field(None, description="Calendar API result")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Event data that was used")
    calendar_link: Optional[str] = Field(None, description="Direct link to the created calendar event")
    event_id: Optional[str] = Field(None, description="Google Calendar event ID")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Calendar event created successfully",
                "calendar_result": {"id": "event123", "status": "confirmed"},
                "event_data": {
                    "summary": "Team Meeting",
                    "date": "2024-01-15",
                    "start_time": "14:30",
                    "location": "Conference Room A"
                },
                "calendar_link": "https://calendar.google.com/event?eid=...",
                "event_id": "event123"
            }
        }


class CompleteWorkflowResponse(ApiResponse):
    """Response model for complete workflow endpoint."""
    email_content: Optional[str] = Field(None, description="Fetched email content")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Extracted event data")
    calendar_result: Optional[Union[Dict[str, Any], str]] = Field(None, description="Calendar creation result")
    identifier: Optional[str] = Field(None, description="The identifier used (message_id or gmail_id)")
    identifier_type: Optional[str] = Field(None, description="Type of identifier used")
    workflow_completed: bool = Field(False, description="Whether the complete workflow finished")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Complete workflow executed successfully",
                "email_content": "Subject: Team Meeting\nFrom: manager@company.com\n\nPlease join our team meeting...",
                "event_data": {
                    "summary": "Team Meeting",
                    "date": "2024-01-15",
                    "start_time": "14:30",
                    "location": "Conference Room A"
                },
                "calendar_result": {"id": "event123", "status": "confirmed"},
                "identifier": "684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail",
                "identifier_type": "message_id",
                "workflow_completed": True
            }
        }


class ErrorResponse(ApiResponse):
    """Response model for error cases."""
    error: str = Field(..., description="Error details")
    error_type: Optional[str] = Field(None, description="Type of error")

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "Operation failed",
                "error": "Gmail API authentication failed",
                "error_type": "AuthenticationError"
            }
        }