#!/bin/bash
# TEMPORARY DEPLOYMENT SCRIPT FOR SECURITY SCANNING TEST
# This contains intentional security issues for testing

set -e

# Hardcoded credentials (UPDATED - should be detected)
export AWS_ACCESS_KEY_ID="AKIA5F6G7H8I9J0K1L2M"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYUpdatedShellKey2024"
export DATABASE_PASSWORD="updated_hardcoded_db_password_789"

# More secret patterns (UPDATED)
DOCKER_PASSWORD="updated_docker_registry_password_456"
GITHUB_TOKEN="ghp_UpdatedGitHubPersonalAccessToken2024ABC"
SLACK_TOKEN="xoxb-updated-slack-bot-token-2024567890"

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