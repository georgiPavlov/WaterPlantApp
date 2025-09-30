#!/bin/bash
# start.sh - WaterPlantApp Start Script

set -e  # Exit on any error

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

# Kill existing Django processes
kill_existing_processes() {
    print_status "Checking for existing Django processes..."
    
    if pgrep -f "manage.py runserver" > /dev/null; then
        print_warning "Found existing Django processes. Stopping them..."
        pkill -f "manage.py runserver" || true
        sleep 2
    fi
    
    print_success "No conflicting processes found"
}

# Check if setup was completed
check_setup() {
    print_status "Checking setup..."
    
    # Check if Django project exists
    if [ ! -d "pycharmtut" ]; then
        print_error "Django project not found. Please run ./setup.sh first"
        exit 1
    fi
    
    # Check if database exists
    if [ ! -f "pycharmtut/db.sqlite3" ]; then
        print_warning "Database not found. Creating migrations..."
        cd pycharmtut
        python3 manage.py makemigrations --settings=pycharmtut.test_settings
        python3 manage.py migrate --settings=pycharmtut.test_settings
        cd ..
    fi
    
    print_success "Setup check complete"
}

# Start Django server
start_django_server() {
    print_status "Starting Django development server..."
    
    cd pycharmtut
    
    # Start server in background
    python3 manage.py runserver 8001 --settings=pycharmtut.test_settings &
    SERVER_PID=$!
    
    # Wait a moment for server to start
    sleep 3
    
    # Check if server is running
    if kill -0 $SERVER_PID 2>/dev/null; then
        print_success "Django server started successfully (PID: $SERVER_PID)"
        echo "Server running on: http://localhost:8001"
        echo "Admin panel: http://localhost:8001/admin/"
        echo "API endpoints: http://localhost:8001/gadget_communicator_pull/api/"
        echo ""
        echo "Press Ctrl+C to stop the server"
        
        # Wait for user to stop
        wait $SERVER_PID
    else
        print_error "Failed to start Django server"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    print_status "Stopping Django server..."
    pkill -f "manage.py runserver" || true
    print_success "Server stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo "🌱 Starting WaterPlantApp..."
    echo "============================"
    
    kill_existing_processes
    check_setup
    start_django_server
}

# Run main function
main "$@"


