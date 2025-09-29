# WaterPlantApp Project Setup Guide

## Overview
WaterPlantApp is a Django-based web application that provides a comprehensive platform for managing water plant automation systems. It serves as the central server that communicates with WaterPlantOperator devices (Raspberry Pi clients) to monitor and control watering operations.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Development Setup](#development-setup)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

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

### 1. Clone the Repository
```bash
git clone https://github.com/georgiPavlov/WaterPlantApp.git
cd WaterPlantApp
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit environment variables
nano .env
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

### 1. Create Database (PostgreSQL)
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE waterplantapp;
CREATE USER waterplantapp_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE waterplantapp TO waterplantapp_user;
\q
```

### 2. Run Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 3. Load Initial Data (Optional)
```bash
# Load fixtures
python manage.py loaddata fixtures/initial_data.json

# Or create sample data
python manage.py shell
>>> from gadget_communicator_pull.models import *
>>> # Create sample devices, plans, etc.
```

## Running the Application

### Development Server
```bash
# Run development server
python manage.py runserver

# Run on specific host and port
python manage.py runserver 0.0.0.0:8000
```

### Production Server
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn pycharmtut.wsgi:application --bind 0.0.0.0:8000

# Run with uWSGI
uwsgi --http :8000 --module pycharmtut.wsgi
```

### Background Tasks (Optional)
```bash
# Run Celery worker
celery -A pycharmtut worker --loglevel=info

# Run Celery beat (for scheduled tasks)
celery -A pycharmtut beat --loglevel=info
```

## Testing

### Run All Tests
```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Run Specific Test Suites
```bash
# Run unit tests
python manage.py test tests.unit

# Run integration tests
python manage.py test tests.integration

# Run cross-integration tests
python manage.py test tests.cross_integration
```

### Run Tests with Pytest
```bash
# Install pytest
pip install pytest pytest-django

# Run tests with pytest
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_models.py -v
```

## Development Setup

### 1. Code Quality Tools
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 .
black .
isort .

# Run type checking
mypy .
```

### 2. Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### 3. IDE Configuration
For PyCharm/IntelliJ:
- Set Python interpreter to virtual environment
- Configure Django support
- Enable code inspection and formatting

For VS Code:
- Install Python extension
- Install Django extension
- Configure settings.json for Django support

## Production Deployment

### 1. Docker Deployment
```bash
# Build Docker image
docker build -t waterplantapp .

# Run container
docker run -d -p 8000:8000 --env-file .env waterplantapp
```

### 2. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/static/files/;
    }

    location /media/ {
        alias /path/to/media/files/;
    }
}
```

### 3. Systemd Service
```ini
[Unit]
Description=WaterPlantApp Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/WaterPlantApp
Environment=PATH=/path/to/WaterPlantApp/venv/bin
ExecStart=/path/to/WaterPlantApp/venv/bin/gunicorn pycharmtut.wsgi:application --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

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

#### 2. Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT setting
python manage.py shell
>>> from django.conf import settings
>>> print(settings.STATIC_ROOT)
```

#### 3. Permission Errors
```bash
# Fix file permissions
chmod -R 755 /path/to/WaterPlantApp
chown -R www-data:www-data /path/to/WaterPlantApp
```

#### 4. Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

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

### Logging Configuration
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Performance Optimization

### 1. Database Optimization
- Use database indexes for frequently queried fields
- Implement database connection pooling
- Use select_related() and prefetch_related() for queries

### 2. Caching
- Implement Redis caching for frequently accessed data
- Use Django's cache framework
- Cache API responses

### 3. Static Files
- Use CDN for static file delivery
- Compress static files
- Implement browser caching

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong, unique secret keys
- Rotate secrets regularly

### 2. Database Security
- Use strong database passwords
- Limit database user permissions
- Enable SSL for database connections

### 3. API Security
- Implement rate limiting
- Use HTTPS in production
- Validate all input data
- Implement proper authentication

## Monitoring and Maintenance

### 1. Health Checks
```bash
# Check application health
curl http://localhost:8000/health/

# Check database connectivity
python manage.py check --database default
```

### 2. Backup Strategy
```bash
# Database backup
pg_dump waterplantapp > backup_$(date +%Y%m%d_%H%M%S).sql

# Media files backup
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

### 3. Log Monitoring
- Monitor application logs for errors
- Set up log rotation
- Implement log aggregation

## Support and Documentation

### Additional Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [WaterPlantOperator Integration Guide](./API_INTEGRATION.md)
- [Testing Guide](./TESTING_GUIDE.md)

### Getting Help
- Check the troubleshooting section above
- Review application logs
- Consult the API documentation
- Contact the development team

This setup guide provides a comprehensive foundation for running WaterPlantApp in both development and production environments. Follow the steps carefully and refer to the troubleshooting section if you encounter any issues.
