#!/usr/bin/env python3
"""
SmartEventAdder Gmail Add-on API

FastAPI backend that provides REST endpoints for Gmail add-on frontend.
Integrates directly with existing SmartEventAdder modules.

Author: SmartEventAdder Project
"""

import sys
import os
import logging
from typing import Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Get project root more reliably for containerized deployment
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import existing SmartEventAdder modules
from modules.event_parser import extract_event_details
from modules.google_calendar import Calendar
from modules.gmail_fetcher import fetch_email_by_message_id_header, fetch_email_by_gmail_id
from modules.google_auth import authenticate_google_services

# Import API-specific components
from api.models.requests import (
    EmailProcessRequest,
    MessageIdRequest,
    GmailIdRequest,
    EventCreateRequest,
    CompleteWorkflowRequest
)
from api.models.responses import (
    ApiResponse,
    ParseEmailResponse,
    FetchEmailResponse,
    CreateEventResponse,
    CompleteWorkflowResponse,
    HealthResponse
)
from api.config import get_settings

# Environment configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
IS_PRODUCTION = ENVIRONMENT.lower() in ['production', 'prod']

# Configure logging for Cloud Run
log_level = logging.INFO if IS_PRODUCTION else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if not IS_PRODUCTION
           else '{"timestamp": "%(asctime)s", "service": "smarteventadder-api", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SmartEventAdder Gmail Add-on API",
    description="REST API for Gmail add-on integration with SmartEventAdder",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for Apps Script
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://script.google.com",
        "https://mail.google.com",
        "http://localhost:3000",  # For local testing
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for settings
settings = get_settings()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error responses."""
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "Internal server error occurred"
        }
    )

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic info."""
    return HealthResponse(
        status="healthy",
        service="SmartEventAdder Gmail Add-on API",
        version="1.0.0"
    )

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Test Google API access
        creds = authenticate_google_services()
        logger.info("Google API authentication successful")

        return HealthResponse(
            status="healthy",
            service="SmartEventAdder Gmail Add-on API",
            version="1.0.0",
            google_auth_status="authenticated"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            service="SmartEventAdder Gmail Add-on API",
            version="1.0.0",
            google_auth_status="failed",
            details=str(e)
        )

@app.post("/api/parse-email", response_model=ParseEmailResponse)
async def parse_email(request: EmailProcessRequest):
    """
    Parse email content and extract event details using Vertex AI.

    This endpoint uses the existing modules.event_parser.extract_event_details function.
    """
    try:
        logger.info(f"Parsing email content ({len(request.email_content)} characters)")

        # Use existing event_parser module
        event_data = extract_event_details(
            project_id=request.project_id or settings.google_cloud_project_id,
            location=request.location or settings.google_cloud_location,
            email_text=request.email_content
        )

        logger.info(f"Event parsed successfully: {event_data.get('summary', 'Unknown')}")

        return ParseEmailResponse(
            success=True,
            event_data=event_data,
            message="Event details extracted successfully"
        )

    except Exception as e:
        logger.error(f"Email parsing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse email: {str(e)}"
        )

@app.post("/api/fetch-email-by-message-id", response_model=FetchEmailResponse)
async def fetch_email_by_message_id(request: MessageIdRequest):
    """
    Fetch email content using Message-ID header.

    This endpoint uses the existing modules.gmail_fetcher.fetch_email_by_message_id_header function.
    """
    try:
        logger.info(f"Fetching email by Message-ID: {request.message_id}")

        # Use existing gmail_fetcher module
        email_content = fetch_email_by_message_id_header(request.message_id)

        logger.info("Email fetched successfully from Gmail")

        return FetchEmailResponse(
            success=True,
            email_content=email_content,
            message_id=request.message_id,
            message="Email fetched successfully"
        )

    except Exception as e:
        logger.error(f"Email fetch failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch email: {str(e)}"
        )

@app.post("/api/fetch-email-by-gmail-id", response_model=FetchEmailResponse)
async def fetch_email_by_gmail_id(request: GmailIdRequest):
    """
    Fetch email content using Gmail API message ID.

    This endpoint uses the existing modules.gmail_fetcher.fetch_email_by_gmail_id function.
    """
    try:
        logger.info(f"Fetching email by Gmail ID: {request.gmail_id}")

        # Use existing gmail_fetcher module
        email_content = fetch_email_by_gmail_id(request.gmail_id)

        logger.info("Email fetched successfully from Gmail")

        return FetchEmailResponse(
            success=True,
            email_content=email_content,
            gmail_id=request.gmail_id,
            message="Email fetched successfully"
        )

    except Exception as e:
        logger.error(f"Email fetch failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch email: {str(e)}"
        )

@app.post("/api/create-event", response_model=CreateEventResponse)
async def create_event(request: EventCreateRequest):
    """
    Create Google Calendar event.

    This endpoint uses the existing modules.google_calendar.Calendar function.
    """
    try:
        logger.info(f"Creating calendar event: {request.event_data.get('summary', 'Unknown')}")

        # Use existing google_calendar module
        result = Calendar(request.event_data)

        logger.info("Calendar event created successfully")

        return CreateEventResponse(
            success=True,
            calendar_result=result,
            event_data=request.event_data,
            message="Calendar event created successfully"
        )

    except Exception as e:
        logger.error(f"Calendar event creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create calendar event: {str(e)}"
        )

@app.post("/api/complete-workflow", response_model=CompleteWorkflowResponse)
async def complete_workflow(request: CompleteWorkflowRequest):
    """
    Complete workflow: Message-ID → Email → Parse → Calendar Event.

    This replicates the main.py workflow via API by using all existing modules.
    """
    try:
        logger.info(f"Starting complete workflow for: {request.message_id or request.gmail_id}")

        # Step 1: Fetch email content
        if request.message_id:
            email_content = fetch_email_by_message_id_header(request.message_id)
            identifier = request.message_id
            identifier_type = "message_id"
        elif request.gmail_id:
            email_content = fetch_email_by_gmail_id(request.gmail_id)
            identifier = request.gmail_id
            identifier_type = "gmail_id"
        else:
            raise ValueError("Either message_id or gmail_id must be provided")

        logger.info("Step 1: Email fetched successfully")

        # Step 2: Parse event details
        event_data = extract_event_details(
            project_id=request.project_id or settings.google_cloud_project_id,
            location=request.location or settings.google_cloud_location,
            email_text=email_content
        )

        logger.info("Step 2: Event details extracted")

        # Step 3: Create calendar event (optional)
        calendar_result = None
        if request.create_event:
            calendar_result = Calendar(event_data)
            logger.info("Step 3: Calendar event created")
        else:
            logger.info("Step 3: Skipped calendar creation (create_event=False)")

        return CompleteWorkflowResponse(
            success=True,
            email_content=email_content,
            event_data=event_data,
            calendar_result=calendar_result,
            identifier=identifier,
            identifier_type=identifier_type,
            workflow_completed=True,
            message="Complete workflow executed successfully"
        )

    except Exception as e:
        logger.error(f"Complete workflow failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Complete workflow failed: {str(e)}"
        )

@app.get("/api/config")
async def get_config():
    """Get current API configuration (non-sensitive data only)."""
    return {
        "google_cloud_location": settings.google_cloud_location,
        "has_project_id": bool(settings.google_cloud_project_id),
        "service": "SmartEventAdder Gmail Add-on API"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")