#!/usr/bin/env python3
"""
Cross-integration test runner for WaterPlantApp and WaterPlantOperator.

This script runs comprehensive cross-integration tests between the Django web application
and the Raspberry Pi automation system, with full macOS compatibility.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_environment():
    """Set up the test environment."""
    print("🔧 Setting up test environment...")
    
    # Add project paths to Python path
    current_dir = Path(__file__).parent
    waterplantapp_path = current_dir.parent / "WaterPlantApp"
    waterplantoperator_path = current_dir.parent / "WaterPlantOperator"
    
    if waterplantapp_path.exists():
        sys.path.insert(0, str(waterplantapp_path))
        print(f"✅ Added WaterPlantApp to Python path: {waterplantapp_path}")
    else:
        print(f"❌ WaterPlantApp not found at: {waterplantapp_path}")
        return False
    
    if waterplantoperator_path.exists():
        sys.path.insert(0, str(waterplantoperator_path))
        print(f"✅ Added WaterPlantOperator to Python path: {waterplantoperator_path}")
    else:
        print(f"❌ WaterPlantOperator not found at: {waterplantoperator_path}")
        return False
    
    return True


def install_dependencies():
    """Install test dependencies."""
    print("📦 Installing test dependencies...")
    
    try:
        # Install cross-integration test dependencies
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        print("✅ Cross-integration test dependencies installed")
        
        # Install WaterPlantApp dependencies
        waterplantapp_requirements = Path(__file__).parent.parent / "WaterPlantApp" / "requirements.txt"
        if waterplantapp_requirements.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(waterplantapp_requirements)
            ], check=True, capture_output=True, text=True)
            print("✅ WaterPlantApp dependencies installed")
        
        # Install WaterPlantOperator test dependencies
        waterplantoperator_requirements = Path(__file__).parent.parent / "WaterPlantOperator" / "requirements-test.txt"
        if waterplantoperator_requirements.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(waterplantoperator_requirements)
            ], check=True, capture_output=True, text=True)
            print("✅ WaterPlantOperator test dependencies installed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False


def run_unit_tests():
    """Run unit tests."""
    print("🧪 Running unit tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_macos_compatibility.py::TestMacOSGPIOCompatibility",
            "test_macos_compatibility.py::TestMacOSPumpCompatibility",
            "test_macos_compatibility.py::TestMacOSServerCheckerCompatibility",
            "test_macos_compatibility.py::TestMacOSServerCommunicatorCompatibility",
            "test_macos_compatibility.py::TestMacOSTimeKeeperCompatibility",
            "test_macos_compatibility.py::TestMacOSModelCompatibility",
            "-v", "--tb=short", "--color=yes"
        ], capture_output=True, text=True)
        
        print("Unit Test Results:")
        print(result.stdout)
        if result.stderr:
            print("Unit Test Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run unit tests: {e}")
        return False


def run_api_tests():
    """Run API integration tests."""
    print("🌐 Running API integration tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_api_integration.py",
            "-v", "--tb=short", "--color=yes"
        ], capture_output=True, text=True)
        
        print("API Test Results:")
        print(result.stdout)
        if result.stderr:
            print("API Test Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run API tests: {e}")
        return False


def run_cross_system_tests():
    """Run cross-system integration tests."""
    print("🔄 Running cross-system integration tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_cross_system_integration.py",
            "-v", "--tb=short", "--color=yes"
        ], capture_output=True, text=True)
        
        print("Cross-System Test Results:")
        print(result.stdout)
        if result.stderr:
            print("Cross-System Test Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run cross-system tests: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("🚀 Running all cross-integration tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            ".", 
            "-v", "--tb=short", "--color=yes", "--durations=10"
        ], capture_output=True, text=True)
        
        print("All Test Results:")
        print(result.stdout)
        if result.stderr:
            print("All Test Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run all tests: {e}")
        return False


def run_with_coverage():
    """Run tests with coverage reporting."""
    print("📊 Running tests with coverage...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            ".", 
            "--cov=.", 
            "--cov-report=html", 
            "--cov-report=term-missing",
            "-v", "--tb=short", "--color=yes"
        ], capture_output=True, text=True)
        
        print("Coverage Test Results:")
        print(result.stdout)
        if result.stderr:
            print("Coverage Test Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run tests with coverage: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Cross-integration test runner")
    parser.add_argument(
        "--test-type", 
        choices=["unit", "api", "cross-system", "all", "coverage"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--install-deps", 
        action="store_true",
        help="Install dependencies before running tests"
    )
    parser.add_argument(
        "--setup-env", 
        action="store_true",
        help="Set up environment before running tests"
    )
    
    args = parser.parse_args()
    
    print("🌱 WaterPlantApp & WaterPlantOperator Cross-Integration Tests")
    print("=" * 60)
    
    # Set up environment if requested
    if args.setup_env:
        if not setup_environment():
            print("❌ Environment setup failed")
            return 1
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            print("❌ Dependency installation failed")
            return 1
    
    # Run tests based on type
    success = True
    
    if args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "api":
        success = run_api_tests()
    elif args.test_type == "cross-system":
        success = run_cross_system_tests()
    elif args.test_type == "coverage":
        success = run_with_coverage()
    else:  # all
        success = run_all_tests()
    
    # Print summary
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests completed successfully!")
        print("🎉 Cross-integration tests passed!")
    else:
        print("❌ Some tests failed!")
        print("🔍 Check the output above for details")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
