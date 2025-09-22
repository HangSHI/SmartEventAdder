# SmartEventAdder

A comprehensive AI-powered event management system that combines a Python backend with a Gmail add-on frontend to automatically parse emails and create Google Calendar events.

## Project Structure

```
SmartEventAdder/
├── modules/                  # Core backend modules
│   ├── __init__.py           # Makes 'modules' a Python package
│   ├── google_auth.py        # The "Key" - Unified OAuth2 authentication for all Google APIs
│   ├── event_parser.py       # The "Brain" - All LLM logic goes here (uses Vertex AI)
│   ├── google_calendar.py    # The "Hands" - All Google Calendar API logic
│   └── gmail_fetcher.py      # The "Eyes" - Gmail API integration for email fetching
│
├── gmail-addon-api/          # Production-ready FastAPI backend
│   ├── api/                  # API implementation
│   │   ├── __init__.py       # Package initialization
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── config.py         # Configuration management
│   │   └── models/           # Request/response models
│   │       ├── __init__.py   # Models package initialization
│   │       ├── requests.py   # API request models
│   │       └── responses.py  # API response models
│   └── tests/                # API-specific tests
│       ├── __init__.py       # Test package initialization
│       └── test_api.py       # FastAPI endpoint tests
│
├── frontend/                 # Gmail add-on frontend
│   └── gmail-addon/          # Google Apps Script code
│       ├── appsscript.json   # Add-on manifest and configuration
│       └── Code.gs           # Main Apps Script code with UI logic
│
├── tests/                    # Comprehensive backend tests
│   ├── __init__.py           # Makes 'tests' a Python package
│   ├── test_main.py          # Unit tests for main.py orchestrator (36 test cases)
│   ├── test_event_parser.py  # Unit tests for event_parser module
│   ├── test_event_parser_integration.py # Integration tests with real Vertex AI API
│   ├── test_google_calendar.py # Unit tests for google_calendar module
│   ├── test_gmail_fetcher.py # Unit tests for gmail_fetcher module
│   └── test_calendar_integration.py # Google Calendar integration tests
│
├── sample_emails/            # Sample email files for testing
│   ├── meeting_invite.txt    # Weekly team meeting example
│   ├── business_meeting.txt  # Formal business meeting example
│   └── casual_event.txt      # Casual company event example
│
├── main.py                   # The "Orchestrator" - Complete CLI workflow
├── run_tests.py              # Test runner script
├── pytest.ini               # Pytest configuration
├── Dockerfile                # Container deployment configuration
├── deploy.sh                 # Cloud deployment script
├── credentials.json          # Your Google API credentials file (not tracked in git)
├── .env                      # Your Google Cloud configuration (not tracked in git)
├── requirements.txt          # Python dependencies
├── .gitignore               # Files to ignore in version control
└── README.md                # This file
```

## Features

### Core Features
- **AI-Powered Event Parsing**: Uses Google Vertex AI (Gemini 1.5 Flash) to extract event information from natural language text
- **Google Calendar Integration**: Automatically creates events in your Google Calendar
- **Gmail API Integration**: Fetch emails directly from Gmail using message IDs or Message-ID headers
- **Unified OAuth 2.0 Authentication**: Dedicated authentication module for all Google APIs with single sign-on

### Multiple Interfaces
- **Gmail Add-on Interface**: Interactive card-based UI directly in Gmail sidebar
- **REST API**: Production-ready FastAPI backend for programmatic access
- **Command Line Interface**: Complete CLI workflow with multiple input methods
- **Web API Documentation**: Auto-generated API docs with interactive testing

### User Experience
- **User-Friendly Gmail Add-on**: Click-to-parse interface with visual feedback
- **Input Validation & Security**: Sanitizes input and validates data before processing
- **User Confirmation**: Review extracted details before creating calendar events
- **Comprehensive Error Handling**: Helpful error messages and recovery suggestions
- **Real-time Processing**: Immediate feedback and progress indicators

### Developer Features
- **Production-Ready API**: FastAPI backend with proper logging, CORS, and error handling
- **Comprehensive Testing**: 77+ test cases covering all functionality
- **Container Deployment**: Docker support for cloud deployment
- **Modular Architecture**: Clean separation between parsing, authentication, and calendar logic

## Setup

This project supports multiple deployment modes: CLI usage, API backend, and Gmail add-on frontend.

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
GOOGLE_CLOUD_LOCATION=asia-northeast1
```

**Note:** The setup script will help you identify your project ID. Tokyo region (`asia-northeast1`) is recommended for users in Japan.

## Usage

### Gmail Add-on Interface (Recommended)

The Gmail add-on provides the most user-friendly experience for parsing emails and creating calendar events directly from Gmail.

#### Setup Gmail Add-on

1. **Deploy API Backend** (required for add-on):
   ```bash
   # Deploy to Google Cloud Run
   ./deploy.sh
   ```

2. **Configure Apps Script**:
   - Go to [script.google.com](https://script.google.com)
   - Create new project and copy code from `frontend/gmail-addon/Code.gs`
   - Update `API_BASE_URL` with your deployed API endpoint
   - Copy manifest from `frontend/gmail-addon/appsscript.json`
   - Enable Gmail API service in Apps Script

3. **Test the Add-on**:
   - Deploy as test add-on in Apps Script
   - Open Gmail and select any email
   - See Smart Event Adder in the right sidebar
   - Click "Parse Event" to extract event details
   - Click "Create Calendar Event" to add to calendar

#### Add-on Features

- **One-Click Parsing**: Extract event details from any email
- **Visual Feedback**: Progress indicators and clear status messages
- **Event Preview**: Review extracted details before creating events
- **Error Handling**: User-friendly error messages with suggestions
- **Real-time Processing**: Immediate AI-powered analysis

### REST API Interface

The FastAPI backend provides programmatic access to SmartEventAdder functionality.

#### Start API Server

```bash
# Development mode
cd gmail-addon-api
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Production deployment
./deploy.sh
```

#### API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Parse Email Content:**
```bash
curl -X POST http://localhost:8000/api/parse-email \
  -H "Content-Type: application/json" \
  -d '{
    "email_content": "Team meeting tomorrow at 2pm in conference room A"
  }'
```

**Create Calendar Event:**
```bash
curl -X POST http://localhost:8000/api/create-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_data": {
      "summary": "Team Meeting",
      "date": "2024-01-15",
      "start_time": "14:00",
      "location": "Conference Room A"
    }
  }'
```

**Complete Workflow (Gmail ID → Event):**
```bash
curl -X POST http://localhost:8000/api/complete-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "gmail_id": "1995b3c89509dde1",
    "create_event": true
  }'
```

#### API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Command Line Interface

The CLI provides direct access to all SmartEventAdder functionality for development and automation.

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

### Gmail Fetcher Module

The `gmail_fetcher.py` module provides Gmail API integration to fetch emails using Message-ID headers:

```python
from modules.gmail_fetcher import fetch_email_by_message_id_header, fetch_email_by_gmail_id

# Method 1: Fetch email using Message-ID header (Recommended)
message_id_header = "684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail"
email_content = fetch_email_by_message_id_header(message_id_header)

# Method 2: Fetch email using Gmail API message ID
gmail_message_id = "1995b3c89509dde1"
email_content = fetch_email_by_gmail_id(gmail_message_id)

# The email_content contains formatted email with subject, from, date, and body
```

### Gmail Message ID Handling

**Important Discovery:** Gmail uses different ID formats for different purposes:

| ID Type | Format | Example | Use Case |
|---------|--------|---------|----------|
| **Gmail URL ID** | 32 chars | `FMfcgzQcpnPVtskckfTVKvTdmrrjVXGf` | Web interface only |
| **Gmail API Message ID** | 16 chars | `1995785e0194fbb3` | API calls |
| **Email Message-ID Header** | Email format | `2b630e07-5cd7-4791-9ff1-a4d0a58a56e3@seg.co.jp` | Email headers |

**To find a message by Message-ID header:**

```python
from modules.gmail_fetcher import search_message_by_message_id_header

# Search for message using Message-ID header (simplified)
message_id_header = '684f4d406f3ab_3af8b03fe4820d99a838379b6@tb-yyk-ai803.k-prd.in.mail'
message = search_message_by_message_id_header(message_id_header)

if message:
    # Process the Gmail API message object
    print(f"Found message: {message.get('id')}")
    # Extract content using extract_email_content(message)
```

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
location = "asia-northeast1"  # Tokyo region

# Extract structured event data
event_details = extract_event_details(project_id, location, email_text)
# Returns: {
#     "summary": "Monthly team meeting",
#     "date": "2024-01-15",
#     "start_time": "14:30",
#     "location": "Conference Room A, 123 Main Street, New York, NY"
# }
```

#### CLI Usage (main.py)

The `main.py` script orchestrates the complete CLI workflow from email to calendar event:

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

#### **Features:**
- **Multiple input methods** (interactive, file, command line, Message-ID header)
- **Automatic Message-ID detection** - Recognizes and fetches emails from Gmail automatically
- **Input sanitization** and validation
- **User confirmation** before creating events
- **Comprehensive error handling** with helpful suggestions
- **Logging** to `smarteventadder.log` for debugging
- **Beautiful console output** with progress indicators

## Testing

This project includes a comprehensive test suite with **77 total test cases** covering all functionality:

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
# Run complete test suite (77 tests)
python -m pytest -v

# Run with coverage report
python -m pytest --cov=modules --cov=main -v

# Run only unit tests (skip integration tests)
python -m pytest -k "not integration" -v

# Use the test runner script
python run_tests.py
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


## Deployment

### API Backend Deployment

The FastAPI backend can be deployed to Google Cloud Run using Docker:

```bash
# Build and deploy
./deploy.sh

# Manual deployment
docker build -t smarteventadder-api .
gcloud run deploy smarteventadder-api --source . --region asia-northeast1
```

### Gmail Add-on Deployment

1. **Development Testing**:
   - Use Apps Script test deployments
   - Deploy as personal add-on for testing

2. **Production Deployment**:
   - Submit to Google Workspace Marketplace
   - Configure OAuth consent screen
   - Complete security review process

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gmail Add-on  │    │   FastAPI Backend │    │  Google APIs    │
│   (Frontend)    │───▶│   (gmail-addon-api)│───▶│                 │
│                 │    │                  │    │ • Gmail API     │
│ • Apps Script   │    │ • REST endpoints │    │ • Calendar API  │
│ • Card UI       │    │ • Request/Response│    │ • Vertex AI     │
│ • User Actions  │    │ • Error handling │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │   Core Modules   │
                    │                  │
                    │ • google_auth.py │
                    │ • event_parser.py│
                    │ • gmail_fetcher.py│
                    │ • google_calendar.py│
                    └──────────────────┘
```

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Keep your `.env` file private and never share API keys
- The `.gitignore` file is configured to exclude sensitive files
- All API calls use HTTPS and proper authentication
- Input validation and sanitization throughout the system
- Error messages designed to avoid information leakage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run the test suite: `python run_tests.py`
4. Ensure all tests pass and coverage is maintained
5. Submit a pull request with detailed description

## License

This project is for educational purposes.