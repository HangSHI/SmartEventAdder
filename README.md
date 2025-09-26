# SmartEventAdder

## 🤖 AI Agent for Email-to-Calendar Automation

**SmartEventAdder is an intelligent AI agent** that processes emails, extracts event information using Gemini, and seamlessly creates Google Calendar events. 

### Agent Capabilities
- **🧠 Intelligent Email Analysis**: Uses Google Vertex AI (Gemini 2.0 Flash-Lite) to understand natural language and extract structured event data
- **🔄 Autonomous Workflow Execution**: Handles the complete pipeline from email input to calendar event creation without manual intervention
- **🌐 Multi-API Integration**: Orchestrates Gmail API, Google Calendar API, and Vertex AI API calls intelligently


## 🚀 Quick Start

**Want to try it immediately?**

1. **Test the API**: `python test_api.py` (basic connectivity test)
2. **Deploy Gmail Add-on**: Copy `frontend/gmail-addon/Code.gs` to [Apps Script](https://script.google.com)
3. **Run Tests**: Copy `frontend/tests/ProductionAPITest.gs` and run `runAllProductionAPITests()`
4. **Use in Gmail**: Deploy as test add-on and try with real emails

**Live Production API**: `https://smarteventadder-api-20081880195.us-central1.run.app`

## Project Structure

```
SmartEventAdder/
├── modules/                  # A folder for all your reusable logic
│   ├── __init__.py           # Makes 'modules' a Python package
│   ├── google_auth.py        # The "Key" - Unified OAuth2 authentication for all Google APIs
│   ├── event_parser.py       # The "Brain" - All LLM logic goes here (uses Vertex AI)
│   ├── google_calendar.py    # The "Hands" - All Google Calendar API logic
│   └── gmail_fetcher.py      # The "Eyes" - Gmail API integration for email fetching
│
├── gmail-addon-api/          # Production Gmail Add-on API Backend
│   ├── api/                  # FastAPI application
│   │   ├── __init__.py       # Makes 'api' a Python package
│   │   ├── main.py           # FastAPI app with REST endpoints
│   │   ├── config.py         # API configuration settings
│   │   └── models/           # Pydantic models for requests/responses
│   │       ├── __init__.py   # Makes 'models' a Python package
│   │       ├── requests.py   # Request models for API endpoints
│   │       └── responses.py  # Response models for API endpoints
│   └── tests/                # Backend API tests
│       ├── __init__.py       # Makes 'tests' a Python package
│       └── test_api.py       # FastAPI endpoint tests
│
├── frontend/                 # Gmail Add-on Frontend (Google Apps Script)
│   ├── gmail-addon/          # Apps Script project files
│   │   ├── Code.gs           # Main Gmail add-on implementation
│   │   └── appsscript.json   # Apps Script configuration
│   └── tests/                # Frontend testing
│       └── ProductionAPITest.gs # Essential API communication tests
│
├── tests/                    # Backend unit and integration tests
│   ├── __init__.py           # Makes 'tests' a Python package
│   ├── test_main.py          # Unit tests for main.py orchestrator (36 test cases)
│   ├── test_event_parser.py  # Unit tests for event_parser module
│   ├── test_event_parser_integration.py # Integration tests with real Vertex AI API
│   ├── test_google_calendar.py # Unit tests for google_calendar module
│   ├── test_gmail_fetcher.py # Unit tests for gmail_fetcher module
│   └── test_calendar_integration.py # Google Calendar integration tests
│
├── main.py                   # The "Orchestrator" - Complete workflow from email to calendar
├── run_tests.py              # Test runner script
├── test_api.py               # Python API tester for command-line testing
├── pytest.ini               # Pytest configuration
├── Dockerfile                # Multi-stage Docker build for Cloud Run deployment
├── deploy.sh                 # Cloud Run deployment script
├── setup_gcloud.sh           # Google Cloud authentication setup script (deprecated - OAuth2 recommended)
├── sample_emails/            # Sample email files for testing
│   ├── meeting_invite.txt    # Weekly team meeting example
│   ├── business_meeting.txt  # Formal business meeting example
│   └── casual_event.txt      # Casual company event example
├── credentials.json          # Your Google API credentials file (not tracked in git)
├── .env                      # Your Google Cloud configuration (not tracked in git)
├── requirements.txt          # A list of your project's Python libraries
├── .gitignore               # Files to ignore in version control
└── README.md                # This file
```

## Features

### Core Functionality
- **Complete Workflow Orchestration**: End-to-end automation from email text to calendar event
- **AI-Powered Event Parsing**: Uses Google Vertex AI (Gemini 2.0 Flash-Lite) to extract event information from natural language text
- **Google Calendar Integration**: Automatically creates events in your Google Calendar
- **Multiple Input Methods**: Support for file input, direct text, interactive mode, and direct Message-ID header input
- **Gmail API Integration**: Fetch emails directly from Gmail using message IDs or Message-ID headers
- **Input Validation & Security**: Sanitizes input and validates data before processing
- **User Confirmation**: Review extracted details before creating calendar events
- **Unified OAuth 2.0 Authentication**: Dedicated authentication module for all Google APIs with single sign-on


## Setup

### 1. Create Virtual Environment

Create and activate a virtual environment named `smart-event-adder`:

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv smart-event-adder

# Activate virtual environment
source smart-event-adder/bin/activate
```

**On Windows:**
```bash
# Create virtual environment
python -m venv smart-event-adder

# Activate virtual environment
smart-event-adder\Scripts\activate
```

### 2. Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the required APIs:
   - **Google Calendar API** (for calendar integration)
   - **Gmail API** (for email fetching)
   - **Vertex AI API** (for AI-powered event parsing)
4. Create **OAuth 2.0 Client ID** credentials:
   - Go to "Credentials" in the API & Services section
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Download the credentials and save as `credentials.json` in the project root



### 4. Environment Variables

Create a `.env` file in the project root and add your configuration:

```env
GOOGLE_CLOUD_PROJECT_ID=your_gcp_project_id_here
GOOGLE_CLOUD_LOCATION=us-central1
```

**Note:** The setup script will help you identify your project ID. The default region is `us-central1` to access the latest Gemini 2.0 Flash-Lite model. The system automatically detects user timezones and creates calendar events in the correct local time regardless of the API region.

## Production Gmail Add-on API

### Live API Endpoints

The SmartEventAdder API is deployed and ready for production use:

- **🌐 Base URL**: `https://smarteventadder-api-20081880195.us-central1.run.app`
- **📚 API Documentation**: `https://smarteventadder-api-20081880195.us-central1.run.app/docs`
- **❤️ Health Check**: `https://smarteventadder-api-20081880195.us-central1.run.app/api/health`

### Available API Endpoints

| Endpoint | Method | Description | Purpose |
|----------|--------|-------------|---------|
| `/` | GET | Root endpoint | Basic service info |
| `/api/health` | GET | Health check | Service status monitoring |
| `/api/parse-email` | POST | Parse email content | Extract event details using Vertex AI |
| `/api/fetch-email-by-message-id` | POST | Fetch by Message-ID | Get email content from Gmail using Message-ID header |
| `/api/fetch-email-by-gmail-id` | POST | Fetch by Gmail ID | Get email content from Gmail using API message ID |
| `/api/create-event` | POST | Create calendar event | Add event to Google Calendar |
| `/api/complete-workflow` | POST | Complete workflow | Full pipeline: fetch → parse → create event |
| `/api/config` | GET | API configuration | Get service configuration (non-sensitive) |

### API Usage Examples

```bash
# Check API health
curl https://smarteventadder-api-20081880195.us-central1.run.app/api/health

# Parse email content
curl -X POST "https://smarteventadder-api-20081880195.us-central1.run.app/api/parse-email" \
  -H "Content-Type: application/json" \
  -d '{"email_content": "Team meeting tomorrow at 2pm in conference room A"}'

# Complete workflow with Message-ID
curl -X POST "https://smarteventadder-api-20081880195.us-central1.run.app/api/complete-workflow" \
  -H "Content-Type: application/json" \
  -d '{"message_id": "your-message-id-here", "create_event": true}'
```

### Gmail Add-on Frontend

The Gmail add-on frontend is built with Google Apps Script and integrates seamlessly with the production API:

- **📍 Location**: `frontend/gmail-addon/Code.gs`
- **🔧 Configuration**: `frontend/gmail-addon/appsscript.json`
- **🧪 Test Suite**: `frontend/tests/ProductionAPITest.gs` (comprehensive API tests)
- **📖 Testing Guide**: Available in `frontend/tests/ProductionAPITest.gs` comments

**Key Features:**
- **Editable Forms**: Users can review and edit AI-extracted event details before calendar creation
- **Enhanced Success Cards**: Direct calendar links and event management
- **Real-time API Integration**: Communicates with production backend using Google Apps Script OAuth
- **Error Handling**: Comprehensive error messages and fallback options
- **Identity Token Authentication**: Uses ScriptApp.getIdentityToken() for secure API communication
- **Base64 Email Decoding**: Robust handling of Gmail API message payloads with multiple encoding methods
- **Multi-Timezone Support**: Automatically detects user timezone and creates calendar events in local time

### 🌍 Multi-Timezone Support

SmartEventAdder automatically handles timezone detection and creates calendar events in the user's local time, regardless of where the API is hosted.

**How it works:**
- **Auto-Detection**: Uses Google Calendar settings, Apps Script session timezone, or locale-based mapping
- **Global Compatibility**: Works for users in Japan (JST), USA (EST/PST), Europe (CET), and more
- **No Configuration**: Zero setup required - timezone is detected automatically
- **Accurate Times**: When a Japanese user says "meeting at 2pm tomorrow", the event is created at 2pm JST

**Supported Timezones:**
- Asia/Tokyo (Japan)
- America/New_York (US East)
- America/Los_Angeles (US West)
- Europe/London (UK)
- Europe/Berlin (Germany)
- Asia/Shanghai (China)
- Australia/Sydney (Australia)
- And more via automatic detection

**Architecture Benefits:**
- **Latest AI Models**: API runs in `us-central1` for access to Gemini 2.0 Flash-Lite
- **Local Time Accuracy**: Calendar events created in user's actual timezone
- **Global Performance**: Low-latency timezone detection using local browser/Google account data

## Usage

### Google Authentication Module

The `google_auth.py` module provides unified authentication for all Google services:

```python
from modules.google_auth import authenticate_google_services

# Get authenticated credentials for all Google APIs
# This works for Gmail, Calendar, and Vertex AI
creds = authenticate_google_services()

# Use credentials with any Google API client
from googleapiclient.discovery import build
gmail_service = build('gmail', 'v1', credentials=creds)
calendar_service = build('calendar', 'v3', credentials=creds)

# Vertex AI also uses the same credentials automatically
```


### Gmail Message ID Handling

**Important Discovery:** Gmail uses different ID formats for different purposes:

| ID Type | Format | Example | Use Case |
|---------|--------|---------|----------|
| **Gmail URL ID** | 32 chars | `FMfcgzQcpnPVtgeckfTVKvTdmrrjVCGf` | Web interface only |
| **Gmail API Message ID** | 16 chars | `1935785e0196fbb3` | API calls |
| **Email Message-ID Header** | Email format | `2b660e07-5cd7-4191-9ff1-a4d0a58a56e3@seg.co.jp` | Email headers |


**Key Limitations:**
- Gmail URL IDs cannot be used directly with Gmail API
- Email Message-ID headers require search-based retrieval
- Only Gmail API message IDs work with direct `messages.get()` calls

### Google Calendar Module

The `google_calendar.py` module provides the `Calendar()` function to create events:

```python
from modules.google_calendar import Calendar

# Event data dictionary
event_data = {
    'summary': 'Meeting with Team',
    'location': 'Conference Room A',
    'date': '2024-01-15',       # Format: YYYY-MM-DD
    'start_time': '14:30'       # Format: HH:MM (24-hour format)
}

# Create the event
Calendar(event_data)
```

### Event Parser Module

The `event_parser.py` module uses Google Vertex AI to parse natural language into event data:

```python
from modules.event_parser import extract_event_details

# Extract event details from natural language text
email_text = """
Please join us for our monthly team meeting on January 15, 2024 at 2:30 PM.
The meeting will be held at Conference Room A, 123 Main Street, New York, NY.
"""

project_id = "your-gcp-project-id"
location = "us-central1"  # Default region for Gemini 2.0 Flash-Lite

# Extract structured event data
event_details = extract_event_details(project_id, location, email_text)
# Returns: {
#     "summary": "Monthly team meeting",
#     "date": "2024-01-15",
#     "start_time": "14:30",
#     "location": "Conference Room A, 123 Main Street, New York, NY"
# }
```

### Main Script (Complete Workflow)

The `main.py` script orchestrates the complete workflow from email to calendar event:

#### **Usage Options:**

```bash
# Interactive mode - enter email content manually
python main.py

# Direct text input
python main.py "Team meeting tomorrow at 2pm in conference room A"

# File input - read email from text file
python main.py sample_emails/meeting_invite.txt

# Message-ID header input - fetch email directly from Gmail
python main.py "684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail"
```

#### **Sample Email Files:**
We provide sample email files for testing:
- `sample_emails/meeting_invite.txt` - Weekly team meeting
- `sample_emails/business_meeting.txt` - Formal business meeting
- `sample_emails/casual_event.txt` - Casual company picnic

#### **Workflow Steps:**
1. **📧 Email Input** - Get email content via file, text, interactive input, or Message-ID header (with automatic Gmail fetching)
2. **🛡️ Input Validation** - Sanitize and validate email content
3. **🤖 AI Processing** - Extract event details using Vertex AI
4. **✅ Data Validation** - Verify extracted information completeness
5. **👀 User Review** - Display extracted details for confirmation
6. **📅 Calendar Creation** - Create Google Calendar event
7. **📊 Results** - Show success/failure with detailed feedback


## Testing

This project includes a comprehensive test suite with **85+ total test cases** covering all functionality:

### Test Suite Overview

| Test File | Test Count | Purpose |
|-----------|------------|---------|
| `test_main.py` | 36 tests | Complete orchestrator workflow testing |
| `test_event_parser.py` | 6 tests | Event parsing unit tests with mocking |
| `test_event_parser_integration.py` | 6 tests | Real Vertex AI API integration tests |
| `test_google_calendar.py` | 5 tests | Google Calendar API unit tests |
| `test_gmail_fetcher.py` | 11 tests | Gmail API unit tests with unified authentication |
| `test_gmail_fetcher_integration.py` | 6 tests | Gmail API integration tests with real data |
| `test_gmail_message_api.py` | 2 tests | Gmail Message-ID header analysis and API exploration |
| `test_calendar_integration.py` | 5 tests | End-to-end calendar integration tests |
| **Backend API Tests** | **Additional** | **FastAPI endpoint testing** |
| `gmail-addon-api/tests/test_api.py` | 10+ tests | FastAPI backend endpoint validation |

### Main Orchestrator Tests (36 test cases)

Run comprehensive unit tests for the main workflow orchestrator:

```bash
# Run all main.py function tests
python -m pytest tests/test_main.py -v

# Run specific test categories
python -m pytest tests/test_main.py::TestMainFunctions -v
python -m pytest tests/test_main.py::TestMainIntegration -v

# Run with coverage report
python -m pytest --cov=main tests/test_main.py
```

**Main.py Test Coverage (36 tests in 2 test classes):**
- **TestMainFunctions** - Core function testing with comprehensive mocking
  - **setup_logging()** - Logging configuration validation
  - **load_environment()** - Environment variable loading (success, missing, defaults)
  - **is_message_id_header()** - Message-ID header detection and validation
  - **get_email_input()** - Multiple input methods (file, text, interactive, Message-ID header, error handling)
  - **validate_email_input()** - Input sanitization, validation, security filtering
  - **validate_extracted_data()** - Data validation, date/time format checking
  - **display_event_details()** - Event display formatting with missing data handling
  - **get_user_confirmation()** - User interaction simulation and validation
  - **create_calendar_event()** - Calendar integration with comprehensive error scenarios
- **TestMainIntegration** - End-to-end workflow integration testing

### Event Parser Tests (6 + 6 = 12 tests)

```bash
# Unit tests with mocking (no external API calls)
python -m pytest tests/test_event_parser.py -v

# Integration tests with real Vertex AI API
python -m pytest tests/test_event_parser_integration.py -v

# Integration tests with verbose output to see AI responses
python -m pytest tests/test_event_parser_integration.py -v -s
```

**Event Parser Test Coverage:**
- **TestEventParser** (6 unit tests) - Mocked AI Platform calls testing JSON parsing, error handling, and response validation
- **TestEventParserIntegration** (6 integration tests) - Real Vertex AI API testing with various email formats and complexity levels

### Gmail Fetcher Tests (11 unit + 6 integration = 17 tests)

```bash
# Run all Gmail fetcher unit tests
python -m pytest tests/test_gmail_fetcher.py -v

# Run Gmail fetcher integration tests
python -m pytest tests/test_gmail_fetcher_integration.py -v

# Run with coverage report
python -m pytest --cov=modules.gmail_fetcher tests/test_gmail_fetcher.py --cov-report=term-missing
```

**Gmail Fetcher Test Coverage:**
- **TestGmailFetcherUnit** (11 tests) - Unit tests with mocked Gmail API calls
  - **Unified authentication** - Tests using the new `google_auth` module
  - **search_message_by_message_id_header()** - Message-ID header search functionality
  - **fetch_message_by_id()** - Gmail API message fetching with error handling
  - **fetch_email_by_message_id_header()** - Complete Message-ID to email content workflow
  - **fetch_email_by_gmail_id()** - Complete Gmail API message ID workflow
  - **extract_email_content()** - Email content extraction from Gmail message objects
  - **extract_message_body()** - Plain text and multipart message handling
  - **strip_html_tags()** - HTML email content processing
- **TestGmailFetcherIntegration** (3 tests) + **TestGmailFetcherRealWorldScenarios** (3 tests) - Real Gmail API integration testing

### Gmail Message API Tests (2 tests)

```bash
# Run Gmail Message-ID header analysis tests
python -m pytest tests/test_gmail_message_api.py -v -s
```

**Gmail Message API Test Coverage:**
- **Direct Gmail API exploration** - Understanding different Gmail ID formats
- **Message-ID header research** - Testing the differences between Gmail URL IDs, API message IDs, and email Message-ID headers
- **Key findings documentation** - Validates that Gmail web interface IDs cannot be used directly with Gmail API

### Gmail API Testing & Analysis

Run Gmail API analysis tests to understand message ID handling:

```bash
# Test Gmail API response structure and real message retrieval
PYTHONPATH=/Users/ko.shi/Projects/SmartEventAdder python tests/test_gmail_api.py

# Test Gmail Message-ID header search functionality
PYTHONPATH=/Users/ko.shi/Projects/SmartEventAdder python tests/test_gmail_message_api.py
```

**Gmail API Test Files:**
- `test_gmail_api.py` - Analyzes Gmail API JSON response structure and demonstrates proper thread/message retrieval
- `test_gmail_message_api.py` - Tests Message-ID header search using `rfc822msgid:` query and demonstrates the differences between Gmail URL IDs, API message IDs, and email Message-ID headers

### Gmail Fetcher Integration Tests

Run integration tests with real Gmail API calls (requires authentication):

```bash
# Run Gmail fetcher integration tests with real Gmail data
python -m pytest tests/test_gmail_fetcher_integration.py -v -s

# Run specific integration test categories
python -m pytest tests/test_gmail_fetcher_integration.py::TestGmailFetcherIntegration -v -s
python -m pytest tests/test_gmail_fetcher_integration.py::TestGmailFetcherRealWorldScenarios -v -s

# Run with coverage report
python -m pytest --cov=modules.gmail_fetcher tests/test_gmail_fetcher_integration.py -v -s
```

**Integration Test Requirements:**
- Valid `credentials.json` file with Gmail API access
- Gmail API enabled in Google Cloud Console
- OAuth2 authentication completed (`token.json` with Gmail scopes)
- Real Gmail message IDs for testing

**Integration Test Coverage:**
- **Real Gmail authentication** - Complete OAuth2 flow testing
- **Message-ID header search** - Search for emails using Message-ID headers with real API
- **Email content fetching** - Retrieve actual emails by Gmail API message ID
- **Complete workflows** - Message-ID header → Email content and Gmail ID → Email content
- **Error handling** - Nonexistent message scenarios
- **Permission verification** - Gmail scope validation

### Google Calendar Tests (5 unit + 5 integration = 10 tests)

```bash
# Run Google Calendar unit tests
python -m pytest tests/test_google_calendar.py -v

# Run calendar integration tests (requires credentials)
python -m pytest tests/test_calendar_integration.py -v
```

**Google Calendar Test Coverage:**
- **TestGoogleCalendarUnit** (5 tests) - Unit tests with mocked Google Calendar API calls
  - **Calendar event creation** - Success scenarios and error handling
  - **DateTime formatting** - Proper timezone and format handling
  - **HTTP error handling** - API error response testing
  - **Missing field validation** - Input validation testing
- **TestGoogleCalendarIntegration** (4 tests) + **TestGoogleCalendarIntegrationManual** (1 test) - Real Calendar API integration
  - **Authentication integration** - OAuth2 flow testing
  - **Event creation with real API** - End-to-end calendar integration
  - **Edge case handling** - Special characters, edge times
  - **Manual OAuth flow testing** - Interactive authentication testing

### Running All Tests

```bash
# Run complete test suite (85+ tests)
python -m pytest -v

# Run with coverage report
python -m pytest --cov=modules --cov=main --cov=gmail-addon-api/api --cov-report=term-missing -v

# Run only unit tests (skip integration tests)
python -m pytest -k "not integration" -v

# Use the comprehensive test runner script
python run_tests.py

# Quick development tests
python run_tests.py quick

# Backend API tests specifically
python run_tests.py api
```

### Test Categories

**Unit Tests (with mocking):**
- No external API calls required
- Fast execution
- Comprehensive function coverage
- Security and validation testing

**Integration Tests (with real APIs):**
- Requires Google Cloud authentication
- Real Vertex AI API calls
- End-to-end workflow validation
- Slower execution but validates actual functionality

### Test Requirements

**For Unit Tests:** No additional setup required
**For Integration Tests:**
- OAuth2 authentication with Google APIs (automatic on first run)
- Valid `.env` file with project configuration
- Internet connection for API calls

**Note:** All integration tests are designed to be safe and use minimal API quotas.

### Backend API Tests

```bash
# Run FastAPI backend tests
python run_tests.py api

# Or run directly with pytest
python -m pytest gmail-addon-api/tests/ -v
```

**Backend API Test Coverage:**
- FastAPI endpoint validation (parse-email, create-event, complete-workflow)
- Request/response model validation with Pydantic
- Authentication and error handling testing
- CORS configuration testing
- Health check and configuration endpoints

**Note:** Backend API tests use mocked dependencies to avoid external API calls during testing.

## Production Deployment

### Deploying the API Backend

The SmartEventAdder API can be deployed to Google Cloud Run using the included deployment scripts:

#### Prerequisites

1. **Google Cloud CLI**: Install and authenticate `gcloud`
2. **Docker**: Required for containerization (handled by Cloud Build)
3. **Google Cloud Project**: With billing enabled
4. **APIs Enabled**: Cloud Run, Cloud Build, Artifact Registry

#### Quick Deployment

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy to Cloud Run (replace with your project ID)
./deploy.sh your-project-id

# Example with specific region (us-central1 is now default)
./deploy.sh your-project-id us-central1
```

#### Deployment Configuration

The deployment uses cost-optimized settings defined in `deploy.sh` and deploys to `us-central1` region by default to access the latest Gemini 2.0 Flash-Lite model:

```bash
# Resource Configuration
--memory 512Mi              # Memory limit (required for 0.17 CPU)
--cpu 0.17                  # Fractional CPU (cost-optimized)
--max-instances 3           # Maximum scaling instances
--min-instances 0           # Scale to zero when not in use
--concurrency 1             # Single request per instance (required for sub-1 CPU)
--timeout 180               # Request timeout (3 minutes for AI processing)

# Environment Variables
ENVIRONMENT=production
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=your-region
```

#### Deployment Output

Successful deployment provides:

```
✅ Deployment completed!
Service URL: https://your-service-url.run.app
Health check: https://your-service-url.run.app/api/health
API docs: https://your-service-url.run.app/docs
```


#### Monitoring and Maintenance

```bash
# Check service status
gcloud run services describe smarteventadder-api --region=us-central1

# View logs
gcloud logs read --service=smarteventadder-api --region=us-central1

# Update service (redeploy)
./deploy.sh your-project-id
```

### Dockerfile Configuration

The multi-stage Docker build (`Dockerfile`) optimizes for production:

```dockerfile
# Features:
- Multi-stage build (reduces image size)
- Non-root user (security)
- Production-optimized Python dependencies
- Health check endpoint
- Proper PYTHONPATH configuration
- Cloud Run port handling (8080)
```

### Frontend Deployment & Testing

The Gmail add-on frontend is deployed to Google Apps Script and connects to the production API.

#### Quick Deployment & Testing

**Step 1: Deploy to Apps Script**

1. **Go to [Apps Script Console](https://script.google.com)**
2. **Create New Project** called "SmartEventAdder"
3. **Copy Files:**
   - Copy `frontend/gmail-addon/Code.gs` → replace `Code.gs`
   - Copy `frontend/gmail-addon/appsscript.json` → replace `appsscript.json`
   - Copy `frontend/tests/ProductionAPITest.gs` → create new file

**Step 2: Test API Communication**

Run these functions in Apps Script:

```javascript
// Test basic connectivity
testProductionAPIConnectivity()

// Test email parsing
testParseEmailAPI()

// Test event creation (safe - no real calendar events)
testCreateEventAPI()

// Test complete workflow
testCompleteWorkflowAPI()

// Test authentication
testAPIAuthentication()

// Test timezone auto-detection
testTimezoneDetection()

// Run all tests at once (includes timezone test)
runAllProductionAPITests()
```

**Step 3: Test Gmail Add-on**

1. **Deploy as Test Add-on:**
   - Click "Deploy" → "Test deployments"
   - Select "Install add-on"
   - Click "Done"

2. **Test in Gmail:**
   - Open Gmail (same browser)
   - Select any email
   - Look for "Smart Event Adder" in right sidebar
   - Click "Parse Event" button
   - Test the editable form fields
   - Click "📅 Add to Calendar"

#### Sample Test Emails

**Meeting Email:**
```
Subject: Weekly Team Meeting
From: manager@company.com

Hi team,

Please join our weekly team meeting on Tuesday, January 16th at 2:30 PM in Conference Room A.

Agenda:
- Project updates
- Next week planning

Best regards,
Management
```

**Appointment Email:**
```
Subject: Dentist Appointment Confirmation
From: dental@clinic.com

Your appointment is confirmed for Thursday, January 18th at 10:00 AM at Downtown Dental, 123 Main St.

Please arrive 15 minutes early.
```

#### Frontend Testing Troubleshooting

**Common Issues:**

1. **"Failed to parse event"**
   - Check API connectivity with `testProductionAPIConnectivity()`
   - Verify production API is running

2. **"Authentication failed"**
   - This is expected - the API works without auth for parsing
   - Calendar creation may require additional setup

3. **"CORS error"**
   - Only occurs outside Apps Script - should not happen in deployment

4. **Gmail add-on not showing**
   - Ensure deployment succeeded
   - Check Gmail permissions in Apps Script
   - Try refreshing Gmail

#### Expected Frontend Test Results

**API Tests:**
- ✅ Connectivity: Should return "healthy" status
- ✅ Parse Email: Should extract event details from sample emails
- ⚠️ Create Event: May fail without full Google Calendar auth (this is normal)
- ✅ Complete Workflow: Should parse email and return event data
- ✅ Timezone Detection: Should detect user's timezone (Asia/Tokyo, America/New_York, etc.)

**Gmail Add-on:**
- ✅ Sidebar appears when viewing emails
- ✅ "Parse Event" button works
- ✅ Editable form fields appear with extracted data
- ✅ User can edit event details before creating
- ✅ Success card shows after event creation
- ✅ Calendar events created in user's local timezone automatically

#### Frontend Files for Deployment

**Essential Files Only:**
```
frontend/
├── gmail-addon/
│   ├── Code.gs                    ← Main add-on code
│   └── appsscript.json           ← Configuration
└── tests/
    └── ProductionAPITest.gs       ← API testing
```

## API Testing Options

### Option 1: Apps Script Testing (Recommended)

**Best for**: Complete Gmail add-on integration testing with proper OAuth context

1. **Copy** `frontend/tests/ProductionAPITest.gs` to Apps Script console
2. **Run** `runAllProductionAPITests()` function
3. **Review** detailed logs with problem identification

**Features:**
- ✅ One-click comprehensive testing
- ✅ Real Gmail add-on environment
- ✅ Proper Google OAuth context
- ✅ Detailed logging and recommendations

### Option 2: Python Command-Line Testing

**Best for**: Quick API health checks and development workflow

```bash
# Install dependencies (if needed)
pip install requests

# Run Python API tests
python test_api.py

# Or use the comprehensive test runner
python run_tests.py api
```

**Features:**
- ✅ Quick command-line testing
- ✅ No Apps Script setup required
- ✅ Good for CI/CD pipelines
- ⚠️ Limited by external API access (no OAuth context)

**Example Output:**
```
🚀 SmartEventAdder API Test Suite
==================================================
connectivity: ✅ PASS
health: ✅ PASS
parse_email: ❌ FAIL (expected without auth)
create_event: ✅ PASS

Overall: 3/4 tests passed
```

### Testing Summary

| Test Method | Environment | OAuth Context | Use Case |
|-------------|-------------|---------------|----------|
| **Apps Script** | Gmail add-on | ✅ Full OAuth | Production testing |
| **Python CLI** | Command line | ❌ External only | Development/CI |

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Keep your `.env` file private and never share API keys
- The `.gitignore` file is configured to exclude sensitive files

## License

This project is for educational purposes.