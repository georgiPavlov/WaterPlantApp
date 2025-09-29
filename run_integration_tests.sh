#!/bin/bash
# run_integration_tests.sh

set -e  # Exit on any error

echo "🧪 Running WaterPlantApp Integration Tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Django server is running
check_django_server() {
    print_status "Checking if Django server is running..."
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/ | grep -q "404\|200\|302"; then
        print_success "Django server is running on port 8001"
    else
        print_warning "Django server is not running. Please start it with:"
        echo "   cd /Users/I336317/SAPDevelop/projects/local/WaterPlantApp/pycharmtut"
        echo "   python3 manage.py runserver 8001 --settings=pycharmtut.test_settings"
        echo ""
        read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
    fi
}

# Run WaterPlantOperator compatibility tests
run_operator_compatibility_tests() {
    print_status "Running WaterPlantOperator compatibility tests..."
    
    cd /Users/I336317/SAPDevelop/projects/local/cross_integration_tests
    
    if python3 -m pytest test_simple_macos_compatibility.py -v; then
        print_success "WaterPlantOperator compatibility tests passed"
    else
        print_error "WaterPlantOperator compatibility tests failed"
        return 1
    fi
}

# Run HTTP API integration tests
run_http_api_tests() {
    print_status "Running HTTP API integration tests..."
    
    cd /Users/I336317/SAPDevelop/projects/local/WaterPlantApp/tests/cross_integration
    
    if python3 -m pytest test_http_api_integration.py -k "test_server_health_check or test_device_api_endpoints or test_plan_api_endpoints or test_status_api_endpoints" -v; then
        print_success "HTTP API integration tests passed"
    else
        print_error "HTTP API integration tests failed"
        return 1
    fi
}

# Run database integration tests
run_database_tests() {
    print_status "Running database integration tests..."
    
    cd /Users/I336317/SAPDevelop/projects/local/WaterPlantApp/tests/cross_integration
    
    if python3 -m pytest test_database_integration.py -k "test_device_synchronization or test_basic_plan_synchronization or test_moisture_plan_synchronization or test_status_synchronization" -v; then
        print_success "Database integration tests passed"
    else
        print_error "Database integration tests failed"
        return 1
    fi
}

# Run all tests
run_all_tests() {
    print_status "Running all integration tests..."
    
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    # Test 1: WaterPlantOperator compatibility
    echo ""
    echo "=========================================="
    echo "Test 1: WaterPlantOperator Compatibility"
    echo "=========================================="
    if run_operator_compatibility_tests; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 2: HTTP API integration
    echo ""
    echo "=========================================="
    echo "Test 2: HTTP API Integration"
    echo "=========================================="
    if run_http_api_tests; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Test 3: Database integration
    echo ""
    echo "=========================================="
    echo "Test 3: Database Integration"
    echo "=========================================="
    if run_database_tests; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
    
    # Summary
    echo ""
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo "Total test suites: $total_tests"
    echo "Passed: $passed_tests"
    echo "Failed: $failed_tests"
    echo "Success rate: $((passed_tests * 100 / total_tests))%"
    
    if [ $failed_tests -eq 0 ]; then
        print_success "All tests passed! 🎉"
        return 0
    else
        print_error "Some tests failed. Please check the output above."
        return 1
    fi
}

# Main execution
main() {
    echo "🧪 WaterPlantApp Integration Test Runner"
    echo "========================================"
    
    check_django_server
    run_all_tests
}

# Run main function
main "$@"
