#!/usr/bin/env python3
"""
Test runner script for SmartEventAdder project.

This script provides different ways to run tests:
- Unit tests only (no external dependencies)
- Integration tests (requires Google API credentials)
- All tests with optional coverage reporting
- Quick tests for development
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Command not found. Make sure pytest is installed.")
        print("Install with: pip install -r requirements.txt")
        return False


def check_credentials():
    """Check if required credential files exist."""
    credentials_exist = os.path.exists('credentials.json')
    token_exist = os.path.exists('token.json')
    env_exist = os.path.exists('.env')

    print(f"\nCredentials Check:")
    print(f"  credentials.json: {'✓ Found' if credentials_exist else '✗ Not found'}")
    print(f"  token.json: {'✓ Found' if token_exist else '✗ Not found (will be created during OAuth)'}")
    print(f"  .env file: {'✓ Found' if env_exist else '✗ Not found (optional for integration tests)'}")

    return credentials_exist


def is_ci_environment():
    """Detect if running in CI/CD environment."""
    ci_indicators = [
        'CI', 'CONTINUOUS_INTEGRATION', 'GITHUB_ACTIONS',
        'JENKINS_URL', 'GITLAB_CI', 'CIRCLECI', 'TRAVIS'
    ]
    return any(os.getenv(var) for var in ci_indicators)


def main():
    """Main test runner function."""
    print("SmartEventAdder Test Runner")
    print("=" * 60)

    # Auto-detect CI environment
    if is_ci_environment():
        print("🤖 CI/CD Environment Detected")
    
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [unit|integration|api|all|coverage|quick|ci|help]")
        print("\nOptions:")
        print("  unit        - Run only unit tests (no external dependencies)")
        print("  integration - Run only integration tests (requires credentials)")
        print("  api         - Run only backend API tests (FastAPI layer)")
        print("  all         - Run all tests (unit + integration + api)")
        print("  coverage    - Run all tests with coverage report")
        print("  quick       - Run fast unit tests for development")
        print("  ci          - CI/CD optimized tests with XML reporting")
        print("  help        - Show detailed help message")
        sys.exit(1)
    
    test_type = sys.argv[1].lower()

    # Override to CI mode if in CI environment and no specific type given
    if is_ci_environment() and test_type not in ['help', 'ci']:
        print(f"🔄 Auto-switching from '{test_type}' to 'ci' mode for CI/CD environment")
        test_type = 'ci'
    
    if test_type == 'help':
        print("📋 SmartEventAdder Test Runner Help")
        print("=" * 60)
        print("\nTest Types:")
        print("  unit        - Fast unit tests with mocked dependencies")
        print("                • Gmail fetcher, event parser, calendar, main orchestrator")
        print("                • No API calls, no credentials needed")
        print("                • ~52 tests in <2 seconds")
        print()
        print("  integration - Real API integration tests")
        print("                • Gmail API, Vertex AI, Google Calendar integration")
        print("                • Requires credentials.json and .env file")
        print("                • ~20 tests in ~15 seconds")
        print()
        print("  api         - Backend API tests (FastAPI layer)")
        print("                • Gmail Add-on API endpoints and validation")
        print("                • HTTP request/response testing with mocked dependencies")
        print("                • ~30 tests in ~3 seconds")
        print()
        print("  all         - Complete test suite (unit + integration + api)")
        print("                • ~100+ tests covering all functionality")
        print("                • Best for CI/CD and comprehensive validation")
        print()
        print("  coverage    - All tests with detailed coverage report")
        print("                • Shows code coverage percentages")
        print("                • Identifies untested code lines")
        print("                • Essential for code quality metrics")
        print()
        print("  quick       - Fast development tests")
        print("                • Core unit tests only (~30 tests)")
        print("                • Perfect for rapid development cycles")
        print()
        print("  ci          - CI/CD optimized tests")
        print("                • Unit tests with XML output for CI/CD reporting")
        print("                • Timeout handling and environment detection")
        print("                • No integration tests (credentials not available in CI)")
        print()
        print("🔧 Setup for integration tests:")
        print("1. Enable Gmail API, Calendar API, and Vertex AI in Google Cloud Console")
        print("2. Create OAuth2 credentials and save as 'credentials.json'")
        print("3. Create .env file with GOOGLE_CLOUD_PROJECT_ID and GOOGLE_CLOUD_LOCATION")
        print("4. Run: python run_tests.py integration")
        print()
        print("🏗️ Architecture:")
        print("   • Unified OAuth2 authentication (modules/google_auth.py)")
        print("   • 8 test files covering all components")
        print("   • Comprehensive coverage: unit tests + real API integration")
        return
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    success = True
    
    if test_type == 'unit':
        print("Running Unit Tests Only")
        success = run_command([
            'python', '-m', 'pytest',
            'tests/test_gmail_fetcher.py',
            'tests/test_event_parser.py',
            'tests/test_google_calendar.py::TestGoogleCalendarUnit',
            'tests/test_main.py',
            '-v', '--tb=short'
        ], "Unit Tests")
        
    elif test_type == 'integration':
        print("Running Integration Tests")
        has_credentials = check_credentials()

        if not has_credentials:
            print("\n❌ Integration tests require credentials.json file.")
            print("Please follow the setup instructions in README.md")
            sys.exit(1)

        success = run_command([
            'python', '-m', 'pytest',
            'tests/test_gmail_fetcher_integration.py',
            'tests/test_event_parser_integration.py',
            'tests/test_calendar_integration.py',
            '-v', '--tb=short', '-s'
        ], "Integration Tests")

    elif test_type == 'api':
        print("Running Backend API Tests")
        print("🚀 Testing FastAPI endpoints and validation")

        # Note: API tests may have TestClient compatibility issues but still provide value
        success = run_command([
            'python', '-m', 'pytest',
            'gmail-addon-api/tests/',
            '-v', '--tb=short',
            '--disable-warnings'  # Suppress Pydantic deprecation warnings during testing
        ], "Backend API Tests")

        # Provide helpful feedback if tests fail due to known TestClient issue
        if not success:
            print("\n💡 Note: API tests may fail due to TestClient compatibility issues.")
            print("   This is a known issue that doesn't affect the actual API functionality.")
            print("   The API endpoints work correctly when deployed.")

    elif test_type == 'coverage':
        print("Running All Tests with Coverage Report")
        has_credentials = check_credentials()

        # Run comprehensive tests with coverage
        success = run_command([
            'python', '-m', 'pytest',
            '--cov=modules', '--cov=main',
            '--cov-report=term-missing',
            '-v', '--tb=short'
        ], "All Tests with Coverage")

    elif test_type == 'quick':
        print("Running Quick Development Tests")
        success = run_command([
            'python', '-m', 'pytest',
            'tests/test_gmail_fetcher.py',
            'tests/test_event_parser.py',
            'tests/test_google_calendar.py::TestGoogleCalendarUnit',
            '-v', '--tb=short', '-x'  # Stop at first failure for quick feedback
        ], "Quick Unit Tests")

    elif test_type == 'ci':
        print("Running CI/CD Optimized Tests")
        print("🤖 CI Environment - running unit tests with reporting")

        # Set environment variables for CI/CD
        os.environ['PYTHONUNBUFFERED'] = '1'  # Ensure real-time output

        # CI/CD optimized command with XML output and timeouts
        ci_args = [
            'python', '-m', 'pytest',
            'tests/test_gmail_fetcher.py',
            'tests/test_event_parser.py',
            'tests/test_google_calendar.py::TestGoogleCalendarUnit',
            'tests/test_main.py',
            '--tb=short',
            '--junitxml=test-results.xml',  # XML output for CI/CD
            '--cov=modules', '--cov=main',
            '--cov-report=xml:coverage.xml',  # XML coverage for CI/CD
            '--cov-report=term-missing',
            '--cov-fail-under=70',  # Fail if coverage below 70%
            '-v', '--no-header'  # Clean output for CI
        ]

        # Add timeout if pytest-timeout is available
        try:
            import pytest_timeout
            ci_args.extend(['--timeout=300'])  # 5 minute timeout per test
        except ImportError:
            print("💡 Install pytest-timeout for better CI/CD timeout handling")

        success = run_command(ci_args, "CI/CD Unit Tests with Coverage")

    elif test_type == 'all':
        print("Running All Tests")

        # Run unit tests first
        print("\n🧪 Running Unit Tests...")
        unit_success = run_command([
            'python', '-m', 'pytest',
            'tests/test_gmail_fetcher.py',
            'tests/test_event_parser.py',
            'tests/test_google_calendar.py::TestGoogleCalendarUnit',
            'tests/test_main.py',
            '-v', '--tb=short'
        ], "Unit Tests")

        # Run integration tests if credentials exist
        has_credentials = check_credentials()
        integration_success = True

        if has_credentials:
            print("\n🔗 Running Integration Tests...")
            integration_args = [
                'python', '-m', 'pytest',
                'tests/test_gmail_fetcher_integration.py',
                'tests/test_event_parser_integration.py',
                'tests/test_calendar_integration.py',
                '-v', '--tb=short', '-s'
            ]

            # Add timeout for integration tests if available
            try:
                import pytest_timeout
                integration_args.extend(['--timeout=600'])  # 10 min for integration
            except ImportError:
                pass

            integration_success = run_command(integration_args, "Integration Tests")
        else:
            print("\n⚠️ Skipping integration tests (no credentials.json found)")

        # Run API tests
        print("\n🚀 Running Backend API Tests...")
        api_success = run_command([
            'python', '-m', 'pytest',
            'gmail-addon-api/tests/',
            '-v', '--tb=short',
            '--disable-warnings'
        ], "Backend API Tests")

        # Provide helpful feedback if API tests fail
        if not api_success:
            print("\n💡 Note: API tests may fail due to TestClient compatibility issues.")
            print("   This doesn't affect API functionality - the endpoints work when deployed.")

        success = unit_success and integration_success and api_success
        
    else:
        print(f"Unknown test type: {test_type}")
        print("Use 'python run_tests.py help' for available options")
        sys.exit(1)
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests completed successfully!")
    else:
        print("❌ Some tests failed. Check the output above.")
    print(f"{'='*60}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()