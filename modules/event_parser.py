import json
import vertexai
from vertexai.generative_models import GenerativeModel
from .google_auth import authenticate_google_services


def extract_event_details(project_id, location, email_text):
    """
    Extract event details from email text using Google Cloud AI Platform Gemini Flash model.

    Uses OAuth2 credentials for authentication instead of default credentials.

    Args:
        project_id (str): GCP project ID
        location (str): GCP location (e.g., "us-central1")
        email_text (str): Email content to parse

    Returns:
        dict: Dictionary containing extracted event details
    """
    # Get OAuth2 credentials
    creds = authenticate_google_services()

    # Initialize Vertex AI with OAuth2 credentials
    vertexai.init(project=project_id, location=location, credentials=creds)

    # Initialize the Gemini 2.0 Flash-Lite model (using the latest model name)
    model = GenerativeModel("gemini-2.0-flash-lite")

    # Create the universal multilingual prompt
    prompt = f"""
You are a universal event extraction assistant. Extract event details from ANY language email and return ONLY a valid JSON object with these keys:

- summary: Event title (preserve original language if non-English, or provide English translation)
- date: Date in YYYY-MM-DD format
- start_time: Time in 24-hour HH:MM format
- location: Location name (preserve original characters/script)

UNIVERSAL DATE/TIME PARSING RULES:
• Dates: Convert ANY format to YYYY-MM-DD
  - English: Aug 22, 2024 / August 22nd / 8/22/2024
  - Japanese: 2024年08月22日 / 令和6年8月22日
  - Chinese: 2024年8月22日 / 二〇二四年八月二十二日
  - European: 22.08.2024 / 22/08/2024
  - ISO: 2024-08-22

• Times: Convert ANY format to 24-hour HH:MM
  - English: 2:30 PM / 2:30pm / 14:30
  - Japanese: 午後2時30分 / 14時30分 / 2時30分
  - Chinese: 下午2点30分 / 14点30分
  - European: 14.30 / 14:30

LOCATION PRESERVATION:
• Keep original script: 白山店, 北京大学, 서울역, Café Berlin
• Include full address if provided
• Preserve business names exactly as written

CONTENT ANALYSIS:
• Identify event type from context (meeting, appointment, reservation, etc.)
• Extract from confirmations, invitations, booking emails
• Handle mixed-language content
• Work with any writing system (Latin, CJK, Arabic, Cyrillic, etc.)

Return ONLY the JSON object. Use null for missing values.

Email content:
{email_text}
"""

    # Generate response
    response = model.generate_content(prompt)

    # Parse the JSON response
    json_response = response.text.strip()

    # Remove markdown code blocks if present
    if json_response.startswith('```json'):
        json_response = json_response.replace('```json\n', '').replace('\n```', '')
    elif json_response.startswith('```'):
        json_response = json_response.replace('```\n', '').replace('\n```', '')

    event_details = json.loads(json_response)

    return event_details