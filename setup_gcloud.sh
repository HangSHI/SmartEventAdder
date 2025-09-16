#!/bin/bash

# Add gcloud to PATH for this session
export PATH="/opt/homebrew/Caskroom/gcloud-cli/538.0.0/google-cloud-sdk/bin:$PATH"

# Google Cloud Setup Script for SmartEventAdder
echo "Setting up Google Cloud authentication for SmartEventAdder..."

# Set the project
echo "Setting project to smarteventadder-471704..."
gcloud config set project smarteventadder-471704

# Authenticate with your personal account
echo "Setting up authentication..."
echo "This will open a browser window for you to sign in with your personal Gmail account."
gcloud auth login

# Set up Application Default Credentials
echo "Setting up Application Default Credentials for your applications..."
echo "This will also open a browser window."
gcloud auth application-default login

# Enable Vertex AI API
echo "Enabling Vertex AI API..."
gcloud services enable aiplatform.googleapis.com

# Set region
echo "Setting default region to Tokyo (asia-northeast1)..."
gcloud config set compute/region asia-northeast1

echo ""
echo "Setup complete! You should now be able to run the integration tests."
echo "Test with: python -m pytest tests/test_event_parser_integration.py -v"