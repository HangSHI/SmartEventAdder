"""
Request models for SmartEventAdder Gmail Add-on API.

These Pydantic models define the structure of incoming API requests.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any


class EmailProcessRequest(BaseModel):
    """Request model for processing email content."""
    email_content: str = Field(
        ...,
        description="The email content to process",
        min_length=1,
        max_length=50000
    )
    project_id: Optional[str] = Field(
        None,
        description="Google Cloud Project ID (optional, uses default if not provided)"
    )
    location: Optional[str] = Field(
        "asia-northeast1",
        description="Google Cloud location for Vertex AI processing"
    )

    @validator('email_content')
    def validate_email_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Email content cannot be empty')
        return v.strip()


class MessageIdRequest(BaseModel):
    """Request model for fetching email by Message-ID header."""
    message_id: str = Field(
        ...,
        description="Email Message-ID header",
        min_length=10,
        max_length=200
    )
    project_id: Optional[str] = Field(
        None,
        description="Google Cloud Project ID (optional)"
    )
    location: Optional[str] = Field(
        "asia-northeast1",
        description="Google Cloud location"
    )

    @validator('message_id')
    def validate_message_id(cls, v):
        if '@' not in v:
            raise ValueError('Message-ID must contain @ symbol')
        if ' ' in v:
            raise ValueError('Message-ID cannot contain spaces')
        return v.strip()


class GmailIdRequest(BaseModel):
    """Request model for fetching email by Gmail API message ID."""
    gmail_id: str = Field(
        ...,
        description="Gmail API message ID (16-character alphanumeric)",
        min_length=16,
        max_length=16
    )
    project_id: Optional[str] = Field(
        None,
        description="Google Cloud Project ID (optional)"
    )
    location: Optional[str] = Field(
        "asia-northeast1",
        description="Google Cloud location"
    )

    @validator('gmail_id')
    def validate_gmail_id(cls, v):
        if not v.isalnum():
            raise ValueError('Gmail ID must be alphanumeric')
        return v.strip()


class EventCreateRequest(BaseModel):
    """Request model for creating calendar events."""
    event_data: Dict[str, Any] = Field(
        ...,
        description="Event data dictionary containing summary, date, time, location, etc."
    )

    @validator('event_data')
    def validate_event_data(cls, v):
        required_fields = ['summary', 'date', 'start_time']
        for field in required_fields:
            if field not in v or not v[field]:
                raise ValueError(f'Event data must contain {field}')
        return v


class CompleteWorkflowRequest(BaseModel):
    """Request model for complete workflow execution."""
    message_id: Optional[str] = Field(
        None,
        description="Email Message-ID header"
    )
    gmail_id: Optional[str] = Field(
        None,
        description="Gmail API message ID"
    )
    project_id: Optional[str] = Field(
        None,
        description="Google Cloud Project ID (optional)"
    )
    location: Optional[str] = Field(
        "asia-northeast1",
        description="Google Cloud location"
    )
    create_event: bool = Field(
        True,
        description="Whether to create calendar event after parsing"
    )

    @validator('message_id', 'gmail_id')
    def validate_identifiers(cls, v, values):
        # At least one identifier must be provided
        if not v and not values.get('message_id') and not values.get('gmail_id'):
            raise ValueError('Either message_id or gmail_id must be provided')
        return v

    class Config:
        schema_extra = {
            "example": {
                "message_id": "684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail",
                "create_event": True
            }
        }