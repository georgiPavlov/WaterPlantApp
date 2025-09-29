#!/usr/bin/env python3
"""
Comprehensive Test Runner for WaterPlantApp Cross-Integration Tests.

This script runs all cross-integration tests including:
- Real integration tests
- HTTP API integration tests
- Database integration tests
- Corner cases and edge conditions
- Performance tests
"""
import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Exit Code: {result.returncode}")
        print(f"Execution Time: {execution_time:.2f} seconds")
        
        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")
        
        return result.returncode == 0, execution_time, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out after 5 minutes")
        return False, 300, "", "Timeout"
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False, 0, "", str(e)

def check_server_running():
    """Check if WaterPlantApp server is running."""
    try:
        import requests
        response = requests.get('http://localhost:8000/admin/', timeout=5)
        return response.status_code in [200, 302, 404]
    except:
        return False

def start_server():
    """Start WaterPlantApp server in background."""
    print("\n🚀 Starting WaterPlantApp server...")
    
    # Change to Django project directory
    django_dir = current_dir.parent.parent / 'pycharmtut'
    
    command = f"cd {django_dir} && python3 manage.py runserver 8000 --settings=pycharmtut.test_settings"
    
    # Start server in background
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    for i in range(30):  # Wait up to 30 seconds
        if check_server_running():
            print("✅ Server is running!")
            return process
        time.sleep(1)
    
    print("❌ Server failed to start")
    process.terminate()
    return None

def stop_server(process):
    """Stop the server process."""
    if process:
        print("\n🛑 Stopping server...")
        process.terminate()
        process.wait()
        print("✅ Server stopped")

def run_simple_compatibility_tests():
    """Run simple macOS compatibility tests."""
    print("\n🧪 Running Simple macOS Compatibility Tests...")
    
    # Temporarily disable Django conftest
    conftest_path = current_dir / 'conftest.py'
    conftest_backup = current_dir / 'conftest.py.bak'
    
    if conftest_path.exists():
        conftest_path.rename(conftest_backup)
    
    try:
        command = "python3 -m pytest test_simple_macos_compatibility.py -v"
        success, execution_time, stdout, stderr = run_command(command, "Simple macOS Compatibility Tests")
        
        if success:
            print("✅ Simple compatibility tests passed!")
        else:
            print("❌ Simple compatibility tests failed!")
        
        return success, execution_time
        
    finally:
        # Restore conftest
        if conftest_backup.exists():
            conftest_backup.rename(conftest_path)

def run_real_integration_tests():
    """Run real integration tests."""
    print("\n🔗 Running Real Integration Tests...")
    
    command = "python3 -m pytest test_real_integration.py -v"
    success, execution_time, stdout, stderr = run_command(command, "Real Integration Tests")
    
    if success:
        print("✅ Real integration tests passed!")
    else:
        print("❌ Real integration tests failed!")
    
    return success, execution_time

def run_http_api_tests():
    """Run HTTP API integration tests."""
    print("\n🌐 Running HTTP API Integration Tests...")
    
    command = "python3 -m pytest test_http_api_integration.py -v"
    success, execution_time, stdout, stderr = run_command(command, "HTTP API Integration Tests")
    
    if success:
        print("✅ HTTP API integration tests passed!")
    else:
        print("❌ HTTP API integration tests failed!")
    
    return success, execution_time

def run_database_tests():
    """Run database integration tests."""
    print("\n🗄️ Running Database Integration Tests...")
    
    command = "python3 -m pytest test_database_integration.py -v"
    success, execution_time, stdout, stderr = run_command(command, "Database Integration Tests")
    
    if success:
        print("✅ Database integration tests passed!")
    else:
        print("❌ Database integration tests failed!")
    
    return success, execution_time

def run_all_tests():
    """Run all cross-integration tests."""
    print("\n🎯 Running All Cross-Integration Tests...")
    
    command = "python3 -m pytest -v"
    success, execution_time, stdout, stderr = run_command(command, "All Cross-Integration Tests")
    
    if success:
        print("✅ All cross-integration tests passed!")
    else:
        print("❌ Some cross-integration tests failed!")
    
    return success, execution_time

def run_performance_tests():
    """Run performance tests."""
    print("\n⚡ Running Performance Tests...")
    
    command = "python3 -m pytest -k 'performance' -v"
    success, execution_time, stdout, stderr = run_command(command, "Performance Tests")
    
    if success:
        print("✅ Performance tests passed!")
    else:
        print("❌ Performance tests failed!")
    
    return success, execution_time

def run_corner_case_tests():
    """Run corner case tests."""
    print("\n🔍 Running Corner Case Tests...")
    
    command = "python3 -m pytest -k 'corner' -v"
    success, execution_time, stdout, stderr = run_command(command, "Corner Case Tests")
    
    if success:
        print("✅ Corner case tests passed!")
    else:
        print("❌ Corner case tests failed!")
    
    return success, execution_time

def generate_test_report(results):
    """Generate a comprehensive test report."""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for success, _ in results.values() if success)
    failed_tests = total_tests - passed_tests
    total_time = sum(execution_time for _, execution_time in results.values())
    
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    
    print(f"\n{'Test Suite':<30} {'Status':<10} {'Time (s)':<10}")
    print("-" * 50)
    
    for test_name, (success, execution_time) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<30} {status:<10} {execution_time:<10.2f}")
    
    if failed_tests == 0:
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
        print(f"Total execution time: {total_time:.2f} seconds")
    else:
        print(f"\n⚠️  {failed_tests} test suite(s) failed")
        print("Check the output above for details")
    
    return failed_tests == 0

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run WaterPlantApp Cross-Integration Tests')
    parser.add_argument('--test', choices=[
        'simple', 'real', 'http', 'database', 'all', 'performance', 'corner'
    ], help='Run specific test suite')
    parser.add_argument('--no-server', action='store_true', help='Skip server startup')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("🧪 WaterPlantApp Cross-Integration Test Runner")
    print("=" * 50)
    
    # Change to test directory
    os.chdir(current_dir)
    
    server_process = None
    results = {}
    
    try:
        # Start server if needed
        if not args.no_server and not check_server_running():
            server_process = start_server()
            if not server_process:
                print("❌ Failed to start server. Exiting.")
                return 1
        
        # Run tests based on arguments
        if args.test == 'simple':
            success, execution_time = run_simple_compatibility_tests()
            results['Simple Compatibility'] = (success, execution_time)
            
        elif args.test == 'real':
            success, execution_time = run_real_integration_tests()
            results['Real Integration'] = (success, execution_time)
            
        elif args.test == 'http':
            success, execution_time = run_http_api_tests()
            results['HTTP API Integration'] = (success, execution_time)
            
        elif args.test == 'database':
            success, execution_time = run_database_tests()
            results['Database Integration'] = (success, execution_time)
            
        elif args.test == 'performance':
            success, execution_time = run_performance_tests()
            results['Performance'] = (success, execution_time)
            
        elif args.test == 'corner':
            success, execution_time = run_corner_case_tests()
            results['Corner Cases'] = (success, execution_time)
            
        else:  # Run all tests
            # Run simple compatibility tests first (fastest)
            success, execution_time = run_simple_compatibility_tests()
            results['Simple Compatibility'] = (success, execution_time)
            
            # Run real integration tests
            success, execution_time = run_real_integration_tests()
            results['Real Integration'] = (success, execution_time)
            
            # Run HTTP API tests (requires server)
            if check_server_running():
                success, execution_time = run_http_api_tests()
                results['HTTP API Integration'] = (success, execution_time)
            else:
                print("⚠️  Skipping HTTP API tests - server not running")
                results['HTTP API Integration'] = (False, 0)
            
            # Run database tests
            success, execution_time = run_database_tests()
            results['Database Integration'] = (success, execution_time)
            
            # Run performance tests
            success, execution_time = run_performance_tests()
            results['Performance'] = (success, execution_time)
            
            # Run corner case tests
            success, execution_time = run_corner_case_tests()
            results['Corner Cases'] = (success, execution_time)
        
        # Generate report
        all_passed = generate_test_report(results)
        
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
        
    finally:
        # Stop server
        if server_process:
            stop_server(server_process)

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
