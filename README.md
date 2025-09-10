# SmartEventAdder

A Python application that uses AI to parse event information and automatically add events to Google Calendar.

## Project Structure

```
Agent_Mail_Output/
├── modules/                  # A folder for all your reusable logic
│   ├── __init__.py           # Makes 'modules' a Python package
│   ├── event_parser.py       # The "Brain" - All LLM logic goes here
│   └── google_calendar.py    # The "Hands" - All Google Calendar API logic
│
├── main.py                   # The "Manager" - Your main script to run tests
├── credentials.json          # Your Google API credentials file (not tracked in git)
├── .env                      # Your secret API keys (not tracked in git)
├── requirements.txt          # A list of your project's Python libraries
├── .gitignore               # Files to ignore in version control
└── README.md                # This file
```

## Features

- **Event Parsing**: Uses AI (Claude) to extract event information from natural language text
- **Google Calendar Integration**: Automatically creates events in your Google Calendar
- **OAuth 2.0 Authentication**: Secure authentication with Google Calendar API
- **JST Timezone Support**: Properly handles Japan Standard Time (JST/UTC+9)
- **1-Hour Event Duration**: Creates events with a default duration of 1 hour

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

### 4. Environment Variables

Create a `.env` file in the project root and add your API keys:

```env
CLAUDE_API_KEY=your_anthropic_api_key_here
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

The `event_parser.py` module will contain AI logic to parse natural language into event data.

### Main Script

Run the main script to test the functionality:

```bash
python main.py
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
- **python-dotenv**: Environment variable management
- **anthropic**: Claude AI API client
- **python-dateutil**: Enhanced date/time handling
- **requests**: HTTP requests library
- **jsonschema**: JSON schema validation

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Keep your `.env` file private and never share API keys
- The `.gitignore` file is configured to exclude sensitive files

## License

This project is for educational purposes.