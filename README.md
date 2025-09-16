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
├── tests/                    # Unit tests for the project
│   ├── __init__.py           # Makes 'tests' a Python package
│   ├── test_event_parser.py  # Unit tests for event_parser module
│   ├── test_google_calendar.py # Unit tests for google_calendar module
│   └── test_integration.py   # Integration tests
│
├── main.py                   # The "Manager" - Your main script to run tests
├── run_tests.py              # Test runner script
├── pytest.ini               # Pytest configuration
├── credentials.json          # Your Google API credentials file (not tracked in git)
├── .env                      # Your secret API keys (not tracked in git)
├── requirements.txt          # A list of your project's Python libraries
├── .gitignore               # Files to ignore in version control
└── README.md                # This file
```

## Features

- **Event Parsing**: Uses Google Vertex AI (Gemini Pro) to extract event information from natural language text
- **Google Calendar Integration**: Automatically creates events in your Google Calendar
- **OAuth 2.0 Authentication**: Secure authentication with Google Calendar API
- **JST Timezone Support**: Properly handles Japan Standard Time (JST/UTC+9)
- **1-Hour Event Duration**: Creates events with a default duration of 1 hour
- **Comprehensive Testing**: Unit tests with mocking for reliable testing without external API calls

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

### 4. Google Cloud Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Vertex AI API
4. Set up authentication for Vertex AI (either through service account keys or Application Default Credentials)

### 5. Environment Variables

Create a `.env` file in the project root and add your configuration:

```env
GOOGLE_CLOUD_PROJECT_ID=your_gcp_project_id_here
GOOGLE_CLOUD_LOCATION=us-central1
```

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
location = "us-central1"

# Extract structured event data
event_details = extract_event_details(project_id, location, email_text)
# Returns: {
#     "summary": "Monthly team meeting",
#     "date": "2024-01-15",
#     "start_time": "14:30",
#     "location": "Conference Room A, 123 Main Street, New York, NY"
# }
```

### Main Script

Run the main script to test the functionality:

```bash
python main.py
```

## Testing

Run the unit tests to verify functionality:

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_event_parser.py -v

# Run tests with coverage
python -m pytest --cov=modules

# Use the test runner script
python run_tests.py
```

## Authentication Flow

1. First run will open a browser for Google OAuth consent
2. Grant permissions to access your Google Calendar
3. A `token.json` file will be created to store your access tokens
4. Subsequent runs will use the stored tokens automatically

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