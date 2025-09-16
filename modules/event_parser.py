import json
from google.cloud import aiplatform
from google.cloud.aiplatform import generative_models


def extract_event_details(project_id, location, email_text):
    """
    Extract event details from email text using Google Cloud AI Platform Gemini Pro model.

    Args:
        project_id (str): GCP project ID
        location (str): GCP location (e.g., "us-central1")
        email_text (str): Email content to parse

    Returns:
        dict: Dictionary containing extracted event details
    """
    # Initialize the AI Platform
    aiplatform.init(project=project_id, location=location)

    # Initialize the Gemini Pro model
    model = generative_models.GenerativeModel("gemini-1.0-pro")

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
    event_details = json.loads(json_response)

    return event_details