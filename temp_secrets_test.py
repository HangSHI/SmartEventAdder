#!/usr/bin/env python3
"""
TEMPORARY FILE FOR SECURITY SCANNING TEST
This file contains intentional fake secrets to test our CI/CD security scanning.
Should be detected by Gitleaks, Bandit, and other security tools.
"""

import os
import requests

# TEST SECRETS - These should be detected by security scanners

# 1. AWS API Keys (more realistic patterns)
AWS_ACCESS_KEY_ID = "AKIA2E2CVDF4HNJ6XKWQ"
AWS_SECRET_ACCESS_KEY = "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"

# 2. GitHub Token (more realistic pattern)
GITHUB_TOKEN = "ghp_2K4jF9xN8mB5cQ7rT3pL6vX1zE4wY0sA9iH"

# 3. Google API Key (should be detected by Gitleaks)
GOOGLE_API_KEY = "AIzaSyDdI0hCZtE6vySjMIjEyAgRabcdefghijk"

# 4. Database credentials (should be detected by Bandit and Gitleaks)
DATABASE_URL = "postgresql://user:password123@localhost:5432/database"
DB_PASSWORD = "super_secret_password_123"

# 5. Private SSH Key (should be detected by Gitleaks)
SSH_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA7qQKqhRwjRKqUaNuTcOJitQx4NlPEyGrNKqG0AhDhPgzWJ0s
... (fake key content) ...
-----END RSA PRIVATE KEY-----"""

# 6. Hardcoded passwords in code (should be detected by Bandit)
def authenticate_user():
    username = "admin"
    password = "hardcoded_password_123"  # Bandit should flag this
    return f"{username}:{password}"

# 7. SQL injection vulnerability (should be detected by Bandit and Semgrep)
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection risk
    return query

# 8. Insecure random (should be detected by Bandit)
import random
def generate_token():
    return random.random()  # Insecure random usage

# 9. Hard-coded JWT secret (should be detected by multiple tools)
JWT_SECRET = "my_super_secret_jwt_key_12345"

# 10. Slack webhook (should be detected by Gitleaks)
SLACK_WEBHOOK = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"

# 11. Cryptocurrency private key (should be detected by Gitleaks)
BITCOIN_PRIVATE_KEY = "5KJvsngHeMpm884wtkJNzQGaCErckhHJBGFsvd3VyK5qMZXj3hS"

# 12. OAuth tokens
OAUTH_TOKEN = "ya29.a0AfH6SMC9nEeq4E7cWm5HnZgJO7G8BwKL_example_token"

# 13. Firebase config (should be detected)
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyC-fake-firebase-key-example123456789",
    "authDomain": "myapp.firebaseapp.com",
    "databaseURL": "https://myapp.firebaseio.com",
    "projectId": "my-firebase-project",
    "storageBucket": "myapp.appspot.com",
    "messagingSenderId": "123456789012"
}

# 14. Email credentials (should be detected)
EMAIL_USERNAME = "admin@company.com"
EMAIL_PASSWORD = "email_password_123"

class TestSecrets:
    """Class with various security issues for testing"""

    def __init__(self):
        # More hardcoded credentials
        self.api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
        self.secret_token = "xoxb-1234567890123-1234567890123-abcdefghijklmnopqrstuvwx"

    def insecure_hash(self, password):
        # Weak hashing (should be detected by Bandit)
        import hashlib
        return hashlib.md5(password.encode()).hexdigest()

    def shell_injection_risk(self, user_input):
        # Shell injection vulnerability (should be detected by Bandit/Semgrep)
        import subprocess
        return subprocess.call(f"echo {user_input}", shell=True)

# Test function with secrets
def main():
    print("This is a test file for security scanning validation")
    print(f"AWS Key: {AWS_ACCESS_KEY_ID}")
    print(f"Database: {DATABASE_URL}")

    # More security issues
    secrets = TestSecrets()
    user_data = get_user_data("1; DROP TABLE users; --")

    return "Testing complete"

if __name__ == "__main__":
    main()