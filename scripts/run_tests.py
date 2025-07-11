#!/usr/bin/env python3
"""
Test runner script for ConstitutionalFlow
This script runs the complete test suite with coverage reporting.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests_with_coverage():
    """Run tests with coverage reporting."""
    print("🧪 Running ConstitutionalFlow Test Suite")
    print("=" * 50)
    
    # Test command with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False

def run_specific_test_category(category):
    """Run tests for a specific category."""
    print(f"🧪 Running {category} tests")
    print("=" * 30)
    
    cmd = [
        sys.executable, "-m", "pytest",
        f"tests/test_{category}.py",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ {category} tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {category} tests failed with exit code {e.returncode}")
        return False

def run_unit_tests():
    """Run only unit tests."""
    print("🧪 Running Unit Tests")
    print("=" * 25)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_constitutional.py",
        "tests/test_feedback.py",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Unit tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Unit tests failed with exit code {e.returncode}")
        return False

def run_integration_tests():
    """Run only integration tests."""
    print("🧪 Running Integration Tests")
    print("=" * 30)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_api.py",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Integration tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Integration tests failed with exit code {e.returncode}")
        return False

def check_test_dependencies():
    """Check if test dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing test dependencies: {', '.join(missing_packages)}")
        print("📦 Installing test dependencies...")
        
        cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
        try:
            subprocess.run(cmd, check=True)
            print("✅ Test dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install test dependencies: {e}")
            return False
    
    return True

def main():
    """Main test runner function."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "unit":
            success = run_unit_tests()
        elif command == "integration":
            success = run_integration_tests()
        elif command == "constitutional":
            success = run_specific_test_category("constitutional")
        elif command == "feedback":
            success = run_specific_test_category("feedback")
        elif command == "api":
            success = run_specific_test_category("api")
        else:
            print(f"❌ Unknown test category: {command}")
            print("Available categories: unit, integration, constitutional, feedback, api")
            return False
    else:
        # Check dependencies first
        if not check_test_dependencies():
            return False
        
        # Run all tests with coverage
        success = run_tests_with_coverage()
    
    if success:
        print("\n📊 Test Summary:")
        print("✅ All tests completed successfully")
        print("📈 Coverage report generated in htmlcov/")
        print("📄 XML coverage report: coverage.xml")
    else:
        print("\n❌ Test Summary:")
        print("❌ Some tests failed")
        sys.exit(1)
    
    return success

if __name__ == "__main__":
    main() 