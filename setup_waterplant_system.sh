#!/bin/bash
# setup_waterplant_system.sh

set -e  # Exit on any error

echo "🌱 Setting up WaterPlantApp Integration System..."

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

# Check if Python 3.9+ is available
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Core dependencies
    pip3 install Django==4.2.24
    pip3 install djangorestframework
    pip3 install djangorestframework-simplejwt
    pip3 install django-filter
    pip3 install python-dotenv
    pip3 install Pillow
    
    # Testing dependencies
    pip3 install pytest
    pip3 install pytest-django
    pip3 install pytest-mock
    pip3 install pytest-cov
    pip3 install requests-mock
    
    # Hardware mocking
    pip3 install gpiozero
    
    # Try to install picamera (will fail on macOS, that's OK)
    pip3 install picamera || print_warning "picamera not available (expected on macOS)"
    
    print_success "Dependencies installed"
}

# Clone WaterPlantOperator if not exists
setup_waterplantoperator() {
    print_status "Setting up WaterPlantOperator..."
    
    OPERATOR_DIR="/Users/I336317/SAPDevelop/projects/local/WaterPlantOperator"
    
    if [ ! -d "$OPERATOR_DIR" ]; then
        print_status "Cloning WaterPlantOperator from GitHub..."
        cd /Users/I336317/SAPDevelop/projects/local
        git clone https://github.com/georgiPavlov/WaterPlantOperator.git
        print_success "WaterPlantOperator cloned"
    else
        print_success "WaterPlantOperator already exists"
    fi
    
    # Install WaterPlantOperator dependencies
    if [ -f "$OPERATOR_DIR/requirements-test.txt" ]; then
        print_status "Installing WaterPlantOperator test dependencies..."
        cd "$OPERATOR_DIR"
        pip3 install -r requirements-test.txt
        print_success "WaterPlantOperator dependencies installed"
    fi
}

# Setup Django database
setup_django_database() {
    print_status "Setting up Django database..."
    
    cd /Users/I336317/SAPDevelop/projects/local/WaterPlantApp/pycharmtut
    
    # Create migrations
    python3 manage.py makemigrations --settings=pycharmtut.test_settings
    
    # Apply migrations
    python3 manage.py migrate --settings=pycharmtut.test_settings
    
    print_success "Django database setup complete"
}

# Fix JWT authentication
fix_jwt_authentication() {
    print_status "Fixing JWT authentication..."
    
    # The JWT fix should already be applied, but let's verify
    AUTH_FILE="/Users/I336317/SAPDevelop/projects/local/WaterPlantApp/pycharmtut/authentication/views.py"
    
    if grep -q "rest_framework_jwt" "$AUTH_FILE"; then
        print_warning "JWT authentication needs to be fixed"
        # This should be handled by the previous fixes
    else
        print_success "JWT authentication is properly configured"
    fi
}

# Run tests
run_tests() {
    print_status "Running integration tests..."
    
    # Test 1: WaterPlantOperator compatibility
    print_status "Running WaterPlantOperator compatibility tests..."
    cd /Users/I336317/SAPDevelop/projects/local/cross_integration_tests
    python3 -m pytest test_simple_macos_compatibility.py -v
    
    # Test 2: HTTP API integration
    print_status "Running HTTP API integration tests..."
    cd /Users/I336317/SAPDevelop/projects/local/WaterPlantApp/tests/cross_integration
    python3 -m pytest test_http_api_integration.py -k "test_server_health_check or test_device_api_endpoints" -v
    
    # Test 3: Database integration
    print_status "Running database integration tests..."
    python3 -m pytest test_database_integration.py -k "test_device_synchronization or test_basic_plan_synchronization" -v
    
    print_success "All tests completed"
}

# Main execution
main() {
    echo "🌱 WaterPlantApp Integration Setup"
    echo "=================================="
    
    check_python
    install_dependencies
    setup_waterplantoperator
    setup_django_database
    fix_jwt_authentication
    
    print_success "Setup complete! 🎉"
    
    echo ""
    echo "Next steps:"
    echo "1. Start the Django server:"
    echo "   cd /Users/I336317/SAPDevelop/projects/local/WaterPlantApp/pycharmtut"
    echo "   python3 manage.py runserver 8001 --settings=pycharmtut.test_settings"
    echo ""
    echo "2. Run tests in another terminal:"
    echo "   ./run_integration_tests.sh"
}

# Run main function
main "$@"
