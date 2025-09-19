# SmartEventAdder

A Python application that uses AI to parse event information and automatically add events to Google Calendar.

## Project Structure

```
SmartEventAdder/
├── modules/                  # A folder for all your reusable logic
│   ├── __init__.py           # Makes 'modules' a Python package
│   ├── event_parser.py       # The "Brain" - All LLM logic goes here (uses Vertex AI)
│   ├── google_calendar.py    # The "Hands" - All Google Calendar API logic
│   └── gmail_fetcher.py      # The "Eyes" - Gmail API integration for email fetching
│
├── tests/                    # Comprehensive unit and integration tests
│   ├── __init__.py           # Makes 'tests' a Python package
│   ├── test_main.py          # Unit tests for main.py orchestrator (31 test cases)
│   ├── test_event_parser.py  # Unit tests for event_parser module
│   ├── test_event_parser_integration.py # Integration tests with real Vertex AI API
│   ├── test_google_calendar.py # Unit tests for google_calendar module
│   ├── test_gmail_fetcher.py # Unit tests for gmail_fetcher module
│   └── test_integration.py   # General integration tests
│
├── main.py                   # The "Orchestrator" - Complete workflow from email to calendar
├── run_tests.py              # Test runner script
├── pytest.ini               # Pytest configuration
├── setup_gcloud.sh           # Google Cloud authentication setup script
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

- **Complete Workflow Orchestration**: End-to-end automation from email text to calendar event
- **AI-Powered Event Parsing**: Uses Google Vertex AI (Gemini 1.5 Flash) to extract event information from natural language text
- **Google Calendar Integration**: Automatically creates events in your Google Calendar
- **Multiple Input Methods**: Support for file input, direct text, interactive mode, and Gmail message ID fetching
- **Gmail API Integration**: Fetch emails directly from Gmail using message IDs or URLs
- **Input Validation & Security**: Sanitizes input and validates data before processing
- **User Confirmation**: Review extracted details before creating calendar events
- **OAuth 2.0 Authentication**: Secure authentication with Google Calendar and Gmail APIs
- **JST Timezone Support**: Properly handles Japan Standard Time (JST/UTC+9)
- **1-Hour Event Duration**: Creates events with a default duration of 1 hour
- **Comprehensive Testing**: 75+ test cases including Gmail fetcher testing (19 tests), Gmail integration tests (9 tests), complete main.py orchestrator testing (31 tests), unit tests with mocking, and integration tests with real APIs
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

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

### 3. Google Calendar API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials and save as `credentials.json` in the project root

### 4. Google Cloud Setup (Automated)

**Easy setup using the provided script:**

```bash
# Run the setup script (will open browser windows for authentication)
./setup_gcloud.sh
```

**Manual setup (if needed):**

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Vertex AI API
4. Set up authentication:
   ```bash
   # Authenticate with your personal Google account
   gcloud auth login

   # Set up Application Default Credentials
   gcloud auth application-default login

   # Set your project
   gcloud config set project YOUR_PROJECT_ID
   ```

### 5. Environment Variables

Create a `.env` file in the project root and add your configuration:

```env
GOOGLE_CLOUD_PROJECT_ID=your_gcp_project_id_here
GOOGLE_CLOUD_LOCATION=asia-northeast1
```

**Note:** The setup script will help you identify your project ID. Tokyo region (`asia-northeast1`) is recommended for users in Japan.

## Usage

### Gmail Fetcher Module

The `gmail_fetcher.py` module provides Gmail API integration to fetch emails using thread IDs from Gmail URLs:

```python
from modules.gmail_fetcher import fetch_gmail_thread_json, extract_thread_id_from_url

# Method 1: Fetch thread directly from Gmail URL (Recommended)
gmail_url = "https://mail.google.com/mail/u/0/#inbox/FMfcgzQcpnHbpQPZzTKQgjzPtdsWrwpr"
thread_data = fetch_gmail_thread_json(gmail_url)

# Method 2: Extract thread ID and process manually
thread_id = extract_thread_id_from_url(gmail_url)
# Note: Thread ID from URL may not directly work with Gmail API

# The fetched thread_data contains complete Gmail API response with messages
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
from modules.gmail_fetcher import authenticate_gmail
from googleapiclient.discovery import build

# Search for message using Message-ID header
creds = authenticate_gmail()
service = build('gmail', 'v1', credentials=creds)

message_id_header = '2b630e07-5cd7-4791-9ff1-a4d0a58a56e3@seg.co.jp'
search_query = f'rfc822msgid:{message_id_header}'

result = service.users().messages().list(userId='me', q=search_query, maxResults=1).execute()
messages = result.get('messages', [])

if messages:
    gmail_message_id = messages[0]['id']
    message = service.users().messages().get(userId='me', id=gmail_message_id, format='full').execute()
    # Process the message...
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
```

#### **Sample Email Files:**
We provide sample email files for testing:
- `sample_emails/meeting_invite.txt` - Weekly team meeting
- `sample_emails/business_meeting.txt` - Formal business meeting
- `sample_emails/casual_event.txt` - Casual company picnic

#### **Workflow Steps:**
1. **📧 Email Input** - Get email content via file, text, interactive input, or Gmail message ID
2. **🛡️ Input Validation** - Sanitize and validate email content
3. **🤖 AI Processing** - Extract event details using Vertex AI
4. **✅ Data Validation** - Verify extracted information completeness
5. **👀 User Review** - Display extracted details for confirmation
6. **📅 Calendar Creation** - Create Google Calendar event
7. **📊 Results** - Show success/failure with detailed feedback

#### **Features:**
- **Multiple input methods** (interactive, file, command line)
- **Input sanitization** and validation
- **User confirmation** before creating events
- **Comprehensive error handling** with helpful suggestions
- **Logging** to `smarteventadder.log` for debugging
- **Beautiful console output** with progress indicators

## Testing

This project includes a comprehensive test suite with **75+ total test cases** covering all functionality:

### Test Suite Overview

| Test File | Test Count | Purpose |
|-----------|------------|---------|
| `test_main.py` | 31 tests | Complete orchestrator workflow testing |
| `test_event_parser.py` | 6 tests | Event parsing unit tests with mocking |
| `test_event_parser_integration.py` | 6 tests | Real Vertex AI API integration tests |
| `test_google_calendar.py` | 8 tests | Google Calendar API unit tests |
| `test_gmail_fetcher.py` | 19 tests | Gmail API integration unit tests (updated) |
| `test_gmail_fetcher_integration.py` | 9 tests | Gmail API integration tests with real data |
| `test_gmail_api.py` | - | Gmail API response analysis and Message-ID testing |
| `test_gmail_message_api.py` | - | Gmail Message-ID header testing and search functionality |
| `test_integration.py` | 5+ tests | End-to-end integration tests |

### Main Orchestrator Tests (31 test cases)

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

**Main.py Test Coverage:**
- **setup_logging()** - Logging configuration validation
- **load_environment()** - Environment variable loading (success, missing, defaults)
- **get_email_input()** - Multiple input methods (file, text, interactive, error handling)
- **validate_email_input()** - Input sanitization, validation, security filtering
- **validate_extracted_data()** - Data validation, date/time format checking
- **display_event_details()** - Event display formatting with missing data handling
- **get_user_confirmation()** - User interaction simulation and validation
- **create_calendar_event()** - Calendar integration with comprehensive error scenarios

### Event Parser Tests (Unit & Integration)

```bash
# Unit tests with mocking (no external API calls)
python -m pytest tests/test_event_parser.py -v

# Integration tests with real Vertex AI API
python -m pytest tests/test_event_parser_integration.py -v

# Integration tests with verbose output to see AI responses
python -m pytest tests/test_event_parser_integration.py -v -s
```

### Gmail Fetcher Tests (19 test cases)

Run comprehensive unit tests for the Gmail API integration module:

```bash
# Run all Gmail fetcher unit tests
python -m pytest tests/test_gmail_fetcher.py -v

# Run specific test categories
python -m pytest tests/test_gmail_fetcher.py::TestGmailFetcherUnit -v
python -m pytest tests/test_gmail_fetcher.py::TestGmailFetcherIntegration -v

# Run with coverage report (93% coverage)
python -m pytest --cov=modules.gmail_fetcher tests/test_gmail_fetcher.py --cov-report=term-missing
```

**Gmail Fetcher Test Coverage:**
- **authenticate_gmail()** - OAuth2 authentication flow testing
- **fetch_email_by_id()** - Email fetching with success, not found, and access denied scenarios
- **fetch_email_by_url()** - Complete Gmail URL to email content workflow (NEW)
- **resolve_gmail_url_to_message_id()** - Gmail URL to API message ID resolution (NEW)
- **extract_email_content()** - Email content extraction from Gmail message objects
- **extract_message_body()** - Plain text and multipart message handling
- **strip_html_tags()** - HTML email content processing
- **validate_message_id()** - Message ID format validation (updated for new formats)
- **extract_message_id_from_url()** - URL parsing for Gmail links (updated regex)

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
- **URL parsing** - Extract message IDs from real Gmail URLs
- **Email fetching** - Retrieve actual emails by message ID
- **Complete workflow** - Gmail URL → Message ID → Email content
- **Error handling** - Nonexistent message ID scenarios
- **Permission verification** - Gmail scope validation

### Google Calendar Tests

```bash
# Run Google Calendar unit tests
python -m pytest tests/test_google_calendar.py -v

# Run calendar integration tests (requires credentials)
python -m pytest tests/test_integration.py -v
```

### Running All Tests

```bash
# Run complete test suite (75+ tests)
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
- Google Cloud authentication (run `./setup_gcloud.sh`)
- Valid `.env` file with project configuration
- Internet connection for API calls

**Note:** All integration tests are designed to be safe and use minimal API quotas.

## Authentication Flow

### Google Calendar Authentication
1. First run will open a browser for Google OAuth consent
2. Grant permissions to access your Google Calendar
3. A `token.json` file will be created to store your access tokens
4. Subsequent runs will use the stored tokens automatically

### Vertex AI Authentication
1. Run `./setup_gcloud.sh` or use `gcloud auth application-default login`
2. Browser will open for Google account authentication
3. Grant permissions for cloud platform access
4. Application Default Credentials will be stored locally
5. All Vertex AI API calls will use these credentials automatically

## Dependencies

- **google-api-python-client**: Google Calendar API client
- **google-auth-httplib2**: Google authentication library
- **google-auth-oauthlib**: OAuth 2.0 flow for Google APIs
- **google-cloud-aiplatform**: Google Vertex AI platform client
- **python-dotenv**: Environment variable management
- **python-dateutil**: Enhanced date/time handling
- **requests**: HTTP requests library
- **jsonschema**: JSON schema validation
- **pytest**: Testing framework
- **pytest-cov**: Test coverage reporting

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Keep your `.env` file private and never share API keys
- The `.gitignore` file is configured to exclude sensitive files

## License

This project is for educational purposes.