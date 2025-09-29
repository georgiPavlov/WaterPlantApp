# WaterPlantApp Project Setup Guide

## Overview
WaterPlantApp is a Django-based web application that provides a platform for managing water plant automation systems. It serves as the central server that communicates with WaterPlantOperator devices (Raspberry Pi clients) to monitor and control watering operations.

## Quick Start
1. **Setup**: Run `./setup.sh` to install dependencies
2. **Start**: Run `./start.sh` to start the server
3. **Test**: Run `./test.sh` to verify everything works

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 2GB RAM
- **Storage**: Minimum 1GB free space
- **Network**: Internet connection for package installation

### Required Software
- Python 3.8+
- pip (Python package installer)
- Git (for version control)
- PostgreSQL (recommended for production) or SQLite (for development)

### Optional Software
- Redis (for caching and background tasks)
- Nginx (for production web server)
- Docker (for containerized deployment)

## Installation

### Automated Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/georgiPavlov/WaterPlantApp.git
cd WaterPlantApp

# Run setup script to install everything
./setup.sh
```

### Manual Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env
```

## Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3
# For PostgreSQL: postgresql://user:password@localhost:5432/waterplantapp

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# File Storage
MEDIA_ROOT=/path/to/media/files
STATIC_ROOT=/path/to/static/files

# Security Settings
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
```

### Django Settings
The main settings are configured in `pycharmtut/settings.py`. Key configurations include:

- **Database**: Configured via `DATABASE_URL` environment variable
- **Static Files**: Served from `STATIC_ROOT` in production
- **Media Files**: Served from `MEDIA_ROOT`
- **Security**: Configured based on `DEBUG` setting
- **CORS**: Configured for API access from WaterPlantOperator devices

## Database Setup

### Automated Setup
```bash
# Run setup script to configure database
./setup.sh
```

### Manual Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Running the Application

### Automated Start (Recommended)
```bash
# Start the server with one command
./start.sh
```

### Manual Start
```bash
# Run development server
python manage.py runserver

# Run on specific host and port
python manage.py runserver 0.0.0.0:8000
```

## Testing

### Automated Testing (Recommended)
```bash
# Run all tests with one command
./test.sh
```

### Manual Testing
```bash
# Run all tests
python manage.py test

# Run specific test suites
python manage.py test tests.unit
python manage.py test tests.integration
python manage.py test tests.cross_integration
```

## Development Setup

### Code Quality Tools
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 .
black .
isort .
```

### IDE Configuration
For PyCharm/IntelliJ:
- Set Python interpreter to virtual environment
- Configure Django support
- Enable code inspection and formatting

For VS Code:
- Install Python extension
- Install Django extension
- Configure settings.json for Django support

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database connection
python manage.py dbshell

# Reset database
python manage.py flush
python manage.py migrate
```

#### 2. Missing Dependencies
```bash
# Run setup script to install all dependencies
./setup.sh
```

#### 3. Permission Errors
```bash
# Make scripts executable
chmod +x setup.sh start.sh test.sh
```

#### 4. Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Debug Mode
Enable debug mode for development:
```python
# In settings.py
DEBUG = True
ALLOWED_HOSTS = ['*']
```

## Support and Documentation

### Additional Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [WaterPlantOperator Integration Guide](./WATERPLANTOPERATOR_INTEGRATION.md)
- [Testing Guide](./HOW_TO_RUN_TESTS.md)

### Getting Help
- Check the troubleshooting section above
- Review application logs
- Consult the API documentation
- Contact the development team

This setup guide provides a foundation for running WaterPlantApp in both development and production environments. Follow the steps carefully and refer to the troubleshooting section if you encounter any issues.
