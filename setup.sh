#!/bin/bash
# setup.sh - WaterPlantApp Setup Script

set -e  # Exit on any error

echo "🌱 Setting up WaterPlantApp..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check Python version
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

# Install dependencies
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
    
    # Hardware mocking (for macOS compatibility)
    pip3 install gpiozero
    
    # Try to install picamera (will fail on macOS, that's OK)
    pip3 install picamera || print_warning "picamera not available (expected on macOS)"
    
    print_success "Dependencies installed"
}

# Setup WaterPlantOperator
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

# Create environment file
create_env_file() {
    print_status "Creating environment file..."
    
    ENV_FILE="/Users/I336317/SAPDevelop/projects/local/WaterPlantApp/.env"
    
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << EOF
SECRET_KEY=django-insecure-test-key-for-development
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EOF
        print_success "Environment file created"
    else
        print_success "Environment file already exists"
    fi
}

# Make scripts executable
make_scripts_executable() {
    print_status "Making scripts executable..."
    
    chmod +x /Users/I336317/SAPDevelop/projects/local/WaterPlantApp/setup.sh
    chmod +x /Users/I336317/SAPDevelop/projects/local/WaterPlantApp/start.sh
    chmod +x /Users/I336317/SAPDevelop/projects/local/WaterPlantApp/test.sh
    
    print_success "Scripts made executable"
}

# Main execution
main() {
    echo "🌱 WaterPlantApp Setup"
    echo "====================="
    
    check_python
    install_dependencies
    setup_waterplantoperator
    setup_django_database
    create_env_file
    make_scripts_executable
    
    print_success "Setup complete! 🎉"
    
    echo ""
    echo "Next steps:"
    echo "1. Start the application: ./start.sh"
    echo "2. Run tests: ./test.sh"
    echo "3. Access the app: http://localhost:8001/gadget_communicator_pull/list/"
}

# Run main function
main "$@"


