#!/usr/bin/env python3
"""
Test runner script for SmartEventAdder project.

This script provides different ways to run tests:
- Unit tests only (no external dependencies)
- Integration tests (requires Google Calendar API credentials)
- All tests
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
    
    print(f"\nCredentials Check:")
    print(f"  credentials.json: {'✓ Found' if credentials_exist else '✗ Not found'}")
    print(f"  token.json: {'✓ Found' if token_exist else '✗ Not found (will be created during OAuth)'}")
    
    return credentials_exist


def main():
    """Main test runner function."""
    print("SmartEventAdder Test Runner")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [unit|integration|all|help]")
        print("\nOptions:")
        print("  unit        - Run only unit tests (no external dependencies)")
        print("  integration - Run only integration tests (requires credentials)")
        print("  all         - Run all tests")
        print("  help        - Show this help message")
        sys.exit(1)
    
    test_type = sys.argv[1].lower()
    
    if test_type == 'help':
        print("Test Types:")
        print("  unit        - Fast tests with mocked dependencies")
        print("  integration - Tests that connect to real Google Calendar API")
        print("  all         - Both unit and integration tests")
        print("\nSetup for integration tests:")
        print("1. Get Google Calendar API credentials from Google Cloud Console")
        print("2. Save as 'credentials.json' in the project root")
        print("3. Run: python run_tests.py integration")
        return
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    success = True
    
    if test_type == 'unit':
        print("Running Unit Tests Only")
        success = run_command([
            'python', '-m', 'pytest', 
            'tests/test_google_calendar.py::TestGoogleCalendarUnit',
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
            'tests/test_integration.py::TestGoogleCalendarIntegration',
            '-v', '--tb=short', '-s'
        ], "Integration Tests")
        
    elif test_type == 'all':
        print("Running All Tests")
        
        # Run unit tests first
        print("\n🧪 Running Unit Tests...")
        unit_success = run_command([
            'python', '-m', 'pytest',
            'tests/test_google_calendar.py::TestGoogleCalendarUnit',
            '-v', '--tb=short'
        ], "Unit Tests")
        
        # Run integration tests if credentials exist
        has_credentials = check_credentials()
        integration_success = True
        
        if has_credentials:
            print("\n🔗 Running Integration Tests...")
            integration_success = run_command([
                'python', '-m', 'pytest',
                'tests/test_integration.py::TestGoogleCalendarIntegration',
                '-v', '--tb=short', '-s'
            ], "Integration Tests")
        else:
            print("\n⚠️ Skipping integration tests (no credentials.json found)")
        
        success = unit_success and integration_success
        
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