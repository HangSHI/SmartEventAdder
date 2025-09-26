#!/usr/bin/env python3
"""
SmartEventAdder - Main Orchestrator

This script orchestrates the complete workflow:
1. Extract information from email text
2. Use Vertex AI to parse event details
3. Create Google Calendar event

Author: SmartEventAdder Project
"""

import os
import sys
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

from modules.event_parser import extract_event_details
from modules.google_calendar import Calendar
from modules.gmail_fetcher import fetch_email_by_message_id_header


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('smarteventadder.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def load_environment() -> Dict[str, str]:
    """Load and validate environment variables."""
    load_dotenv()

    config = {
        'project_id': os.getenv('GOOGLE_CLOUD_PROJECT_ID'),
        'location': os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    }

    # Validate required configuration
    if not config['project_id']:
        raise ValueError(
            "GOOGLE_CLOUD_PROJECT_ID not found in .env file. "
            "Please run ./setup_gcloud.sh to configure your environment."
        )

    return config


def is_message_id_header(text: str) -> bool:
    """Check if text looks like a Message-ID header."""
    text = text.strip()

    # Message-ID headers typically contain @ and end with a domain-like string
    if '@' not in text:
        return False

    # Should not contain spaces (Message-IDs are single tokens)
    if ' ' in text:
        return False

    # Should not be too short or too long
    if len(text) < 10 or len(text) > 200:
        return False

    # Should end with something that looks like a domain or server identifier
    parts = text.split('@')
    if len(parts) != 2:
        return False

    local_part, domain_part = parts

    # Both local part and domain part should be non-empty
    if not local_part or not domain_part:
        return False

    # Domain part should contain at least one dot or be a server identifier
    if '.' not in domain_part and '-' not in domain_part:
        return False

    return True


def get_email_input() -> str:
    """Get email content from various input sources."""
    if len(sys.argv) > 1:
        # Command line argument
        if sys.argv[1].endswith('.txt'):
            # File input
            try:
                with open(sys.argv[1], 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                print(f"Error: File '{sys.argv[1]}' not found.")
                sys.exit(1)
        elif is_message_id_header(sys.argv[1]):
            # Message-ID header input
            message_id = sys.argv[1]
            print(f"📨 Detected Message-ID header: {message_id}")
            print("🔍 Fetching email content from Gmail...")
            try:
                email_content = fetch_email_by_message_id_header(message_id)
                print("✅ Email content fetched successfully!")
                return email_content
            except Exception as e:
                print(f"❌ Failed to fetch email: {str(e)}")
                print("\n💡 Suggestions:")
                print("   1. Ensure Gmail API is enabled and credentials are set up")
                print("   2. Check that the Message-ID exists in your Gmail")
                print("   3. Verify you have proper Gmail API permissions")
                sys.exit(1)
        else:
            # Direct text argument
            return sys.argv[1]

    # Interactive input
    print("📧 Enter your email content (press Ctrl+D when finished):")
    print("─" * 60)
    try:
        lines = []
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
        return '\n'.join(lines)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)


def validate_email_input(email_text: str) -> str:
    """Validate and sanitize email input."""
    if not email_text or not email_text.strip():
        raise ValueError("Email content cannot be empty.")

    # Basic sanitization
    email_text = email_text.strip()

    # Remove potentially dangerous content
    dangerous_patterns = ['<script', '</script>', 'javascript:', 'data:']
    for pattern in dangerous_patterns:
        email_text = email_text.replace(pattern, '')

    # Limit length to prevent abuse
    max_length = 10000
    if len(email_text) > max_length:
        print(f"⚠️  Email content truncated to {max_length} characters.")
        email_text = email_text[:max_length]

    # Check minimum length
    if len(email_text.strip()) < 20:
        raise ValueError("Email content too short. Please provide more detailed email content.")

    return email_text


def validate_extracted_data(event_data: Dict) -> Dict:
    """Validate and clean extracted event data."""
    required_keys = ['summary', 'date', 'start_time', 'location']

    # Ensure all required keys exist
    for key in required_keys:
        if key not in event_data:
            event_data[key] = None

    # Basic validation
    if event_data.get('date'):
        # Validate date format (YYYY-MM-DD)
        try:
            from datetime import datetime
            datetime.strptime(event_data['date'], '%Y-%m-%d')
        except ValueError:
            print(f"⚠️  Invalid date format: {event_data['date']}")
            event_data['date'] = None

    if event_data.get('start_time'):
        # Validate time format (HH:MM)
        try:
            from datetime import datetime
            datetime.strptime(event_data['start_time'], '%H:%M')
        except ValueError:
            print(f"⚠️  Invalid time format: {event_data['start_time']}")
            event_data['start_time'] = None

    return event_data


def display_event_details(event_data: Dict) -> None:
    """Display extracted event details to user."""
    print("\n" + "=" * 60)
    print("🤖 EXTRACTED EVENT DETAILS")
    print("=" * 60)

    print(f"📋 Summary:    {event_data.get('summary') or '❌ Not found'}")
    print(f"📅 Date:       {event_data.get('date') or '❌ Not found'}")
    print(f"🕐 Time:       {event_data.get('start_time') or '❌ Not found'}")
    print(f"📍 Location:   {event_data.get('location') or '❌ Not found'}")
    print("=" * 60)


def get_user_confirmation(event_data: Dict) -> bool:
    """Get user confirmation before creating calendar event."""
    # Check if we have minimum required data
    missing_fields = []
    critical_fields = ['summary', 'date', 'start_time']

    for field in critical_fields:
        if not event_data.get(field):
            missing_fields.append(field)

    if missing_fields:
        print(f"\n⚠️  Missing critical information: {', '.join(missing_fields)}")
        print("Cannot create calendar event without this information.")
        return False

    print(f"\n🤔 Do you want to create this calendar event? (y/n): ", end="")
    try:
        response = input().strip().lower()
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return False


def create_calendar_event(event_data: Dict, logger: logging.Logger) -> bool:
    """Create Google Calendar event with error handling."""
    try:
        logger.info("Creating Google Calendar event...")
        result = Calendar(event_data)

        if result:
            print("\n✅ SUCCESS! Calendar event created successfully!")
            return True
        else:
            print("\n❌ Failed to create calendar event.")
            return False

    except Exception as e:
        logger.error(f"Error creating calendar event: {str(e)}")
        print(f"\n❌ Error creating calendar event: {str(e)}")

        # Provide helpful suggestions
        if "credentials" in str(e).lower():
            print("\n💡 Suggestion: Run the following to set up Google Calendar authentication:")
            print("   1. Place your credentials.json file in the project root")
            print("   2. Run the script again to complete OAuth flow")

        return False


def main():
    """Main orchestrator function."""
    print("🚀 SmartEventAdder - AI-Powered Calendar Event Creator")
    print("=" * 60)

    # Set up logging
    logger = setup_logging()
    logger.info("SmartEventAdder started")

    try:
        # Step 1: Load environment configuration
        logger.info("Loading environment configuration...")
        config = load_environment()
        print(f"✅ Environment loaded (Project: {config['project_id']}, Region: {config['location']})")

        # Step 2: Get email input
        logger.info("Getting email input...")
        email_text = get_email_input()

        # Step 3: Validate input
        logger.info("Validating email input...")
        email_text = validate_email_input(email_text)
        print(f"✅ Email content validated ({len(email_text)} characters)")

        # Step 4: Extract event details using Vertex AI
        print("\n🤖 Analyzing email with Vertex AI...")
        logger.info("Calling Vertex AI for event extraction...")

        try:
            event_data = extract_event_details(
                project_id=config['project_id'],
                location=config['location'],
                email_text=email_text
            )
            print("✅ AI analysis completed")
            logger.info(f"Event extracted: {event_data}")

        except Exception as e:
            logger.error(f"Vertex AI extraction failed: {str(e)}")
            print(f"\n❌ AI analysis failed: {str(e)}")

            # Provide helpful suggestions
            if "authentication" in str(e).lower() or "credentials" in str(e).lower():
                print("\n💡 Suggestion: Run ./setup_gcloud.sh to set up authentication")

            sys.exit(1)

        # Step 5: Validate extracted data
        logger.info("Validating extracted event data...")
        event_data = validate_extracted_data(event_data)

        # Step 6: Display results to user
        display_event_details(event_data)

        # Step 7: Get user confirmation
        if not get_user_confirmation(event_data):
            print("\n❌ Operation cancelled by user.")
            logger.info("Operation cancelled by user")
            sys.exit(0)

        # Step 8: Create calendar event
        success = create_calendar_event(event_data, logger)

        if success:
            logger.info("SmartEventAdder completed successfully")
            print(f"\n🎉 Event '{event_data['summary']}' added to your calendar!")
        else:
            logger.error("SmartEventAdder failed to create calendar event")
            sys.exit(1)

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        print(f"\n❌ Configuration Error: {str(e)}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user. Goodbye!")
        logger.info("Operation cancelled by user (KeyboardInterrupt)")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\n💡 Please check the log file 'smarteventadder.log' for more details.")
        sys.exit(1)


if __name__ == "__main__":
    main()