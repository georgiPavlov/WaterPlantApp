# WaterPlantApp - Django Web Application

A comprehensive Django web application for managing water plant automation systems. This application serves as the server/dashboard component that works in conjunction with the WaterPlantOperator Raspberry Pi system.

## 🌱 Overview

WaterPlantApp provides a web-based interface for:
- Managing water plant automation devices
- Creating and scheduling watering plans
- Monitoring device status and water levels
- Viewing historical data and analytics
- Sending email notifications
- API endpoints for device communication

## 🏗️ Architecture

The application follows Django best practices with a modular structure:

```
pycharmtut/
├── gadget_communicator_pull/          # Main Django app
│   ├── models/                        # Data models
│   ├── views/                         # View controllers
│   ├── water_serializers/             # API serializers
│   ├── forms/                         # Django forms
│   ├── templates/                     # HTML templates
│   └── constants/                     # Application constants
├── pycharmtut/                        # Django project settings
└── tests/                             # Comprehensive test suite
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Django 3.2+
- PostgreSQL (recommended) or SQLite
- Redis (for caching, optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/georgiPavlov/WaterPlantApp.git
   cd WaterPlantApp
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - Web interface: http://localhost:8000
   - Admin interface: http://localhost:8000/admin
   - API documentation: http://localhost:8000/api/docs/

## 📊 Features

### Device Management
- **Device Registration**: Register and manage water plant automation devices
- **Real-time Status**: Monitor device connection status and health
- **Water Level Tracking**: Track water levels and container capacity
- **Moisture Monitoring**: Monitor soil moisture levels
- **Location Management**: Track device physical locations

### Watering Plans
- **Basic Plans**: Simple one-time watering plans
- **Moisture Plans**: Intelligent plans based on soil moisture thresholds
- **Time-based Plans**: Scheduled watering with multiple time slots
- **Plan Execution**: Automatic and manual plan execution
- **Plan History**: Track plan execution history

### Monitoring & Analytics
- **Dashboard**: Real-time overview of all devices and plans
- **Historical Data**: Water level and moisture level history
- **Charts & Graphs**: Visual representation of data trends
- **Alerts**: Email notifications for critical events
- **Status Tracking**: Detailed execution status and error logging

### API Integration
- **RESTful API**: Complete API for device communication
- **Authentication**: Secure API authentication
- **Rate Limiting**: API rate limiting for security
- **Webhooks**: Event-driven notifications
- **Documentation**: Comprehensive API documentation

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/waterplantapp

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_RATE_LIMIT=1000/hour
```

### Database Configuration

#### PostgreSQL (Recommended)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'waterplantapp',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### SQLite (Development)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## 🧪 Testing

The application includes a comprehensive test suite:

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test modules
python manage.py test tests.unit.test_models
python manage.py test tests.integration.test_api

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Structure

- **Unit Tests**: Test individual components and models
- **Integration Tests**: Test component interactions
- **API Tests**: Test API endpoints and serializers
- **Fixtures**: Reusable test data

## 📚 API Documentation

### Authentication

The API uses token-based authentication:

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token in requests
curl -H "Authorization: Token your_token_here" \
  http://localhost:8000/api/devices/
```

### Key Endpoints

#### Devices
- `GET /api/devices/` - List all devices
- `POST /api/devices/` - Create new device
- `GET /api/devices/{id}/` - Get device details
- `PUT /api/devices/{id}/` - Update device
- `DELETE /api/devices/{id}/` - Delete device

#### Plans
- `GET /api/plans/basic/` - List basic plans
- `GET /api/plans/moisture/` - List moisture plans
- `GET /api/plans/time/` - List time plans
- `POST /api/plans/basic/` - Create basic plan
- `POST /api/plans/moisture/` - Create moisture plan
- `POST /api/plans/time/` - Create time plan

#### Status
- `GET /api/status/` - List status entries
- `POST /api/status/` - Create status entry
- `GET /api/status/{id}/` - Get status details

### Example API Usage

```python
import requests

# Get all devices
response = requests.get(
    'http://localhost:8000/api/devices/',
    headers={'Authorization': 'Token your_token_here'}
)
devices = response.json()

# Create a new basic plan
plan_data = {
    'name': 'Morning Watering',
    'water_volume': 200,
    'plan_type': 'basic'
}
response = requests.post(
    'http://localhost:8000/api/plans/basic/',
    json=plan_data,
    headers={'Authorization': 'Token your_token_here'}
)
```

## 🚀 Deployment

### Production Setup

1. **Set up production database:**
   ```bash
   # PostgreSQL
   createdb waterplantapp_prod
   ```

2. **Configure production settings:**
   ```python
   # settings/production.py
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'waterplantapp_prod',
           # ... other settings
       }
   }
   ```

3. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "pycharmtut.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/static/files/;
    }
}
```

## 🔒 Security

### Security Features

- **Authentication**: Token-based API authentication
- **Authorization**: Role-based access control
- **Input Validation**: Comprehensive input validation
- **SQL Injection Protection**: Django ORM protection
- **XSS Protection**: Template auto-escaping
- **CSRF Protection**: CSRF tokens for forms
- **Rate Limiting**: API rate limiting
- **HTTPS**: SSL/TLS encryption support

### Security Best Practices

1. **Environment Variables**: Store sensitive data in environment variables
2. **Secret Key**: Use a strong, unique secret key
3. **Database Security**: Use strong database passwords
4. **HTTPS**: Always use HTTPS in production
5. **Regular Updates**: Keep dependencies updated
6. **Backup**: Regular database backups

## 📈 Monitoring

### Health Checks

The application includes health check endpoints:

- `GET /health/` - Basic health check
- `GET /health/db/` - Database connectivity check
- `GET /health/redis/` - Redis connectivity check (if configured)

### Logging

Configure logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'waterplantapp.log',
        },
    },
    'loggers': {
        'gadget_communicator_pull': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests:**
   ```bash
   python manage.py test
   ```
5. **Commit your changes:**
   ```bash
   git commit -m "Add your feature"
   ```
6. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check the comprehensive documentation
- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Join community discussions
- **Email**: Contact the maintainers

### Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**: Check database credentials and connectivity
2. **Email Not Working**: Verify email configuration and credentials
3. **API Authentication**: Ensure correct token format and permissions
4. **Static Files**: Run `collectstatic` command for production

## 🔄 Changelog

### Version 2.0.0 (Latest)
- Enhanced models with comprehensive validation
- Improved serializers with type hints
- Added comprehensive test suite
- Enhanced API documentation
- Improved security features
- Added monitoring and health checks

### Version 1.0.0
- Initial release
- Basic device management
- Simple watering plans
- Basic API endpoints

## 🙏 Acknowledgments

- Django community for the excellent framework
- Contributors and testers
- WaterPlantOperator project for the hardware integration
- Open source libraries and tools used

---

**WaterPlantApp** - Making plant care smarter and more automated! 🌱💧