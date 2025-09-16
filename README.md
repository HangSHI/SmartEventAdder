# SmartEventAdder

A Python application that uses AI to parse event information and automatically add events to Google Calendar.

## Project Structure

```
SmartEventAdder/
├── modules/                  # A folder for all your reusable logic
│   ├── __init__.py           # Makes 'modules' a Python package
│   ├── event_parser.py       # The "Brain" - All LLM logic goes here (uses Vertex AI)
│   └── google_calendar.py    # The "Hands" - All Google Calendar API logic
│
├── tests/                    # Unit and integration tests for the project
│   ├── __init__.py           # Makes 'tests' a Python package
│   ├── test_event_parser.py  # Unit tests for event_parser module
│   ├── test_event_parser_integration.py # Integration tests with real Vertex AI API
│   ├── test_google_calendar.py # Unit tests for google_calendar module
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
- **Multiple Input Methods**: Support for file input, direct text, and interactive mode
- **Input Validation & Security**: Sanitizes input and validates data before processing
- **User Confirmation**: Review extracted details before creating calendar events
- **OAuth 2.0 Authentication**: Secure authentication with Google Calendar API
- **JST Timezone Support**: Properly handles Japan Standard Time (JST/UTC+9)
- **1-Hour Event Duration**: Creates events with a default duration of 1 hour
- **Comprehensive Testing**: Both unit tests with mocking and integration tests with real Vertex AI API calls
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
1. **📧 Email Input** - Get email content via file, text, or interactive input
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

### Unit Tests (with mocking)
Run the unit tests to verify functionality without external API calls:

```bash
# Run unit tests only
python -m pytest tests/test_event_parser.py -v

# Run all unit tests
python -m pytest -k "not integration" -v

# Run tests with coverage
python -m pytest --cov=modules tests/test_event_parser.py
```

### Integration Tests (with real APIs)
Run integration tests that make actual calls to Vertex AI:

```bash
# Run integration tests (requires authentication)
python -m pytest tests/test_event_parser_integration.py -v

# Run with verbose output to see AI responses
python -m pytest tests/test_event_parser_integration.py -v -s
```

### All Tests
```bash
# Run all tests
python -m pytest

# Use the test runner script
python run_tests.py
```

**Note:** Integration tests require Google Cloud authentication (see setup steps above).

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