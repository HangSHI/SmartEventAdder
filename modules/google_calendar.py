from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .google_auth import authenticate_google_services

def Calendar(event_data):
    """
    Create an event on the user's primary Google Calendar.
    
    Args:
        event_data (dict): Dictionary containing event details with keys:
            - summary (str): Event title
            - location (str): Event location
            - date (str): Event date in YYYY-MM-DD format
            - start_time (str): Event start time in HH:MM format
    """
    try:
        # Authenticate and build the service
        creds = authenticate_google_services()
        service = build('calendar', 'v3', credentials=creds)
        
        # Parse date and time
        event_date = event_data['date']  # Expected format: YYYY-MM-DD
        start_time = event_data['start_time']  # Expected format: HH:MM
        
        # Create datetime objects for JST timezone
        start_datetime_str = f"{event_date}T{start_time}:00+09:00"  # JST is UTC+9
        start_datetime = datetime.fromisoformat(start_datetime_str.replace('+09:00', ''))
        end_datetime = start_datetime + timedelta(hours=1)
        
        # Format as RFC3339 with JST timezone
        start_rfc3339 = f"{event_date}T{start_time}:00+09:00"
        end_rfc3339 = f"{end_datetime.strftime('%Y-%m-%d')}T{end_datetime.strftime('%H:%M')}:00+09:00"
        
        # Create event object
        event = {
            'summary': event_data['summary'],
            'location': event_data['location'],
            'start': {
                'dateTime': start_rfc3339,
                'timeZone': 'Asia/Tokyo',
            },
            'end': {
                'dateTime': end_rfc3339,
                'timeZone': 'Asia/Tokyo',
            },
        }
        
        # Create the event
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        
        # Print confirmation with event link
        event_link = event_result.get('htmlLink')
        print(f"Event created successfully!")
        print(f"Event: {event_data['summary']}")
        print(f"Date: {event_data['date']} at {event_data['start_time']} JST")
        print(f"Location: {event_data['location']}")
        print(f"Link: {event_link}")
        
        return event_result
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    except Exception as error:
        print(f"An unexpected error occurred: {error}")
        return None