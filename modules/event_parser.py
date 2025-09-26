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

    # Create the prompt
    prompt = f"""
Extract the following event details from the email text below and return ONLY a valid JSON object string with these keys:

- summary: A concise title for the event
- date: The date in YYYY-MM-DD format
- start_time: The time in 24-hour HH:MM format
- location: The address or place name

If any value is not found, use null for that key.

Return ONLY the JSON object, no other text or explanation.

Email text:
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