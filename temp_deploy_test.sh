#!/bin/bash
# TEMPORARY DEPLOYMENT SCRIPT FOR SECURITY SCANNING TEST
# This contains intentional security issues for testing

set -e

# Hardcoded credentials (should be detected)
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export DATABASE_PASSWORD="hardcoded_db_password_123"

# More secret patterns
DOCKER_PASSWORD="docker_registry_password_123"
GITHUB_TOKEN="ghp_fake_github_personal_access_token_123"
SLACK_TOKEN="xoxb-fake-slack-bot-token-1234567890"

echo "Starting deployment with secrets..."

# Docker login with hardcoded password (security issue)
echo "$DOCKER_PASSWORD" | docker login -u myusername --password-stdin

# Git operations with token in URL (should be detected)
git clone https://oauth2:$GITHUB_TOKEN@github.com/user/repo.git

# Database operations with password in command line (security issue)
mysql -u root -p$DATABASE_PASSWORD -e "SELECT * FROM users;"

# API calls with tokens in URLs (should be detected)
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user

# Slack notification with webhook (should be detected)
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Deployment complete"}' \
  https://hooks.slack.com/services/T1234567/B1234567/fake_webhook_token_123

echo "Deployment completed"